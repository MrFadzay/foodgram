import os

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Импорт ингредиентов из CSV файла'

    def handle(self, *args, **options):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.dirname(base_dir)))))
        csv_file = os.path.join(os.getcwd(), 'data', 'ingredients.csv')

        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                ingredients_to_create = []

                for line in file:
                    line = line.strip()
                    self.stdout.write(f'Обработка строки: {line}')

                    try:
                        name, measurement_unit = line.split(',')
                        ingredients_to_create.append(
                            Ingredient(
                                name=name.strip(),
                                measurement_unit=measurement_unit.strip()
                            )
                        )
                    except ValueError as e:
                        self.stdout.write(
                            self.style.WARNING(
                                f'Пропуск строки "{line}": {str(e)}'
                            )
                        )
                        continue

                if ingredients_to_create:
                    Ingredient.objects.bulk_create(
                        ingredients_to_create,
                        ignore_conflicts=True
                    )
                    count = len(ingredients_to_create)
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'Импортировано {count} ингредиентов'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING('Нет ингредиентов для импорта')
                    )

        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(
                    f'Файл {csv_file} не найден'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'Ошибка при импорте ингредиентов: {e}'
                )
            )
