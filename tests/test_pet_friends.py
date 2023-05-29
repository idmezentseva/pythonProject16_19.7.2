from api import PetFriends
from settings import valid_email, valid_password
import os

pf = PetFriends()


# Тест 1:
def test_get_api_key_for_valid_user(email=valid_email, password=valid_password):
    status, result = pf.get_api_key(email, password)
    assert status == 200
    assert 'key' in result


# Тест 2:
def test_get_all_pets_with_valid_key(filter=''):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)
    assert status == 200
    assert len(result['pets']) > 0


# Тест 3:
def test_add_new_pet_with_valid_data(name='Black', animal_type='mainecoon',
                                     age='1', pet_photo='images/foto_cat.jpg'):
    """Проверяем что можно добавить питомца с корректными данными"""

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name


# Тест 4:
def test_successful_delete_self_pet():
    """Проверяем возможность удаления питомца"""

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Суперкот", "кот", "3", "images/foto_cat.jpg")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Берём id первого питомца из списка и отправляем запрос на удаление
    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)

    # Ещё раз запрашиваем список своих питомцев
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем что статус ответа равен 200 и в списке питомцев нет id удалённого питомца
    assert status == 200
    assert pet_id not in my_pets.values()


# Тест 5:
def test_successful_update_self_pet_info(name='Black', animal_type='mainecoon', age=1):
    """Проверяем возможность обновления информации о питомце"""

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Еслди список не пустой, то пробуем обновить его имя, тип и возраст
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

        # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
        assert status == 200
        assert result['name'] == name
    else:
        # если спиок питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("There is no my pets")


# Тест 6:
def test_add_new_pet_without_photo(name='Black', animal_type='mainecoon', age='1'):
    """Проверяем что можно добавить питомца без фото с корректными данными
       Запрашиваем ключ api и сохраняем в переменую auth_key"""
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet_without_photo(auth_key, name, animal_type, age)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name


# Тест 7:
def test_add_pet_photo(pet_photo='images/foto_cat.jpg'):
    """Проверяем что можно добавить фото питомца.
    Получаем полный путь изображения питомца и сохраняем в переменную pet_photo"""
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, 'my_pets')

    # Проверяем, если список своих питомцев пустой, то добавляем нового и снова запрашиваем список своих питомцев
    if len(my_pets['pets']) > 0:
        status, result = pf.add_pet_photo(auth_key, my_pets['pets'][0]['id'], pet_photo)
        assert status == 200
        assert result['pet_photo'] is not None
    else:
        raise Exception('There is no my pets')


# Тест 8: xfail (баг в api)
def test_add_new_pet_with_invalid_data(name='Black', animal_type='mainecoon',
                                       age='abc', pet_photo='images/foto_cat.jpg'):
    """Негативный сценарий. Добавление питомца, содержащим слово в переменной age.
        Тест не будет пройден, если питомец будет добавлен на сайт с данным значением age"""

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)
    assert status == 400
    assert result['name'] == name


# Тест 9:
def test_invalid_add_pet_photo(pet_photo='images/foto_cat.jpg'):
    """Проверяем, что нельзя добавить фото несуществующему питомцу"""
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    pet_id = '9C4AEC87'
    status, _ = pf.add_pet_photo(auth_key, pet_id, pet_photo)
    assert status == 500


# Тест 10: xfail (баг в api)
def test_add_pet_with_invalid_data(name='?/}]{abc', animal_type='mainecoon',
                                   age='1', pet_photo='images/foto_cat.jpg'):
    """Негативный тест на допуск спецсимволов в имени"""
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, _ = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)
    assert status == 400
