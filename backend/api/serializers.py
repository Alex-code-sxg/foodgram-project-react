import base64

from django.core.files.base import ContentFile
from djoser.serializers import UserSerializer as DjoserUserSerializer
from rest_framework import serializers

from recipes.models import Ingredient, IngredientsInRecipe, Recipe, Tag
from users.models import Subscribe, User


class Base64ImageField(serializers.ImageField):
    '''Сериализатор для кодировки изображения base64'''
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name=f'temp.{ext}')
        return super().to_internal_value(data)


class UserSerializer(DjoserUserSerializer):
    '''Сериализатор модели User'''
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return (user.follower.filter(author=obj).exists()
                and user.is_authenticated)


class TagSerializer(serializers.ModelSerializer):
    '''Сериализатор модели Tag'''
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    '''Сериализатор модели Ingredient'''
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientsInRecipeSerializer(serializers.ModelSerializer):
    '''Сериализатор модели Ingredient в рецептах'''
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True
    )

    class Meta:
        model = IngredientsInRecipe
        fields = ('id', 'name', 'amount', 'measurement_unit')

    def to_representation(self, instance):
        '''Метод для количества ингридиентов'''
        data = IngredientSerializer(instance.ingredient).data
        data['amount'] = instance.amount
        return data


class RecipeReadSerializer(serializers.ModelSerializer):
    '''Сериализатор для чтения рецептов'''
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientsInRecipeSerializer(
        many=True, source='ingredientsinrecipe_set', read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')

    def get_is_favorited(self, obj):
        '''Метод для избранного'''
        user = self.context.get('request').user
        return (Recipe.objects.filter(
            favorites__user=user, id=obj.id).exists()
            and user.is_authenticated)

    def get_is_in_shopping_cart(self, obj):
        '''Метод для корзины'''
        user = self.context.get('request').user
        return (Recipe.objects.filter(shopping_cart__user=user,
                id=obj.id).exists() and user.is_authenticated)


class RecipeCreateSerializer(serializers.ModelSerializer):
    '''Сериализатор для создания нового рецепта'''
    image = Base64ImageField()
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    author = UserSerializer(read_only=True)
    ingredients = IngredientsInRecipeSerializer(
        source='ingredientsinrecipe_set',
        many=True
    )

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'name', 'image',
                  'text', 'cooking_time')

    def ingredients_create(self, ingredients, recipe):
        '''Метод для создания ингридиентов'''
        ingredients_list = [
            IngredientsInRecipe(
                ingredient=ingredient['id'],
                recipe=recipe,
                amount=ingredient['amount']
            ) for ingredient in ingredients
        ]
        IngredientsInRecipe.objects.bulk_create(ingredients_list)

    def validate(self, data):
        '''Валидация данных (наличие ингридиентов, количество, уникальность,
        теги)'''
        ingredients = data.get('ingredientsinrecipe_set')
        if not ingredients:
            raise serializers.ValidationError(
                {'errors': 'Добавьте хотя бы один ингредиент в рецепт'}
            )
        validated_ingredients = []
        for ingredient in ingredients:
            amount = ingredient['amount']
            if amount <= 0:
                raise serializers.ValidationError(
                    {
                        'errors': ('Количество ингредиента должно быть '
                                   'больше 0')
                    }
                )
            if ingredient in validated_ingredients:
                raise serializers.ValidationError(
                    'Ингредиенты должны быть уникальными.'
                )
            validated_ingredients.append(ingredient)
        tags = data['tags']
        if not tags:
            raise serializers.ValidationError(
                'В рецепте должен быть хотя бы один тег'
            )
        validated_tags = []
        for tag in tags:
            validated_tags.append(id)
        if len(validated_tags) != len(validated_tags):
            raise serializers.ValidationError(
                'Теги не должны повторяться.'
            )
        return data

    def create(self, validated_data):
        '''Метод для создания рецепта'''
        ingredients = validated_data.pop('ingredientsinrecipe_set')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.ingredients_create(
            ingredients=ingredients,
            recipe=recipe
        )
        return recipe

    def update(self, instance, validated_data):
        '''Метод для редактирования рецепта'''
        IngredientsInRecipe.objects.filter(recipe=instance).delete()
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredientsinrecipe_set')
        instance.tags.set(tags)
        self.ingredients_create(
            ingredients=ingredients,
            recipe=instance
        )
        return super().update(instance=instance, validated_data=validated_data)


class RecipeSubscribesSerializer(serializers.ModelSerializer):
    '''Сериализатор добавление рецепта в избранное'''
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(UserSerializer):
    '''Сериализатор подписки на автора'''
    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source='author.recipes.count')

    class Meta:
        model = Subscribe
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        '''Метод проверки наличия подписки'''
        return Subscribe.objects.filter(
            user=obj.user, author=obj.author
        ).exists()

    def get_recipes(self, obj):
        '''Сериализатор подписки на автора'''
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        queryset = Recipe.objects.filter(author=obj.author)
        if limit:
            queryset = queryset[:int(limit)]
        return RecipeSubscribesSerializer(queryset, many=True).data


class FavoriteCartSerializer(serializers.ModelSerializer):
    '''Сериализатор для избранного'''
    name = serializers.ReadOnlyField(source='recipe.name')
    image = Base64ImageField(source='recipe.image')
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')
