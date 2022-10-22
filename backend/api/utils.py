from django.http import HttpResponse


def get_shopping_list(ingredient_list):
    '''Метод для формирования списка ингридиентов для скачивания'''
    temp_shopping_cart = {}
    for ingredient in ingredient_list:
        name = ingredient[0]
        temp_shopping_cart[name] = {
            'amount': ingredient[2],
            'measurement_unit': ingredient[1]
        }
        shopping_cart = ["Список покупок\n\n"]
        for key, value in temp_shopping_cart.items():
            shopping_cart.append(f'{key} - {value["amount"]} '
                                 f'{value["measurement_unit"]}\n')
    response = HttpResponse(
        shopping_cart, content_type='text.txt; charset=utf-8'
    )
    response['Content-Disposition'] = ('attachment; '
                                       'filename="shopping_list.txt"')
    return response
