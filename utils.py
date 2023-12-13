import json
import datetime
import random
from rich import box
from rich.table import Table
from rich.console import Console
from rich.markdown import Markdown


class RWData:
    """
        Read/Write and Control data todo
    """

    def __init__(self, path: str = 'data.json'):
        self.path = path
        self.data = {}

    def pull_data(self) -> None:
        with open('./data.json', 'r') as File:
            self.data = json.load(File)

    def push_data(self) -> None:
        with open('./data.json', 'w') as File:
            json.dump(self.data, File, indent=4)

    def category_list(self) -> list[str]:
        return [k for k in self.data.keys()]

    def add_category(self, category_name: str) -> int:
        if category_name in self.data.keys():
            return -1

        self.data[category_name] = {
            'todo': [],
            'last_id': 0
        }
        self.push_data()
        return 0

    def remove_category(self, category_name: str) -> int:
        if category_name not in self.data.keys():
            return -1

        del self.data[category_name]
        self.push_data()
        return 0

    def todo_list(self, category_name: str) -> list:
        return [todo for todo in self.data[category_name]['todo']]

    def todo_add(self, category_name: str, text: str) -> int:
        last_id = self.data[category_name]['last_id']
        new_id = last_id + 1
        self.data[category_name]['last_id'] = new_id

        if category_name not in self.data.keys():
            return -1

        self.data[category_name]['todo'].append(
            {
                'id': new_id,
                'stat': False,
                'text': text
            }
        )
        self.push_data()
        return 0

    def todo_remove(self, category_name: str, todo_id: int) -> int:
        if category_name not in self.data.keys():
            return -1

        for index, item in enumerate(self.data[category_name]['todo']):
            if item['id'] == todo_id:
                del self.data[category_name]['todo'][index]
                self.push_data()
                return 0

        return -2

    def todo_done(self, category_name: str, todo_id: int) -> int:
        if category_name not in self.data.keys():
            return -1

        for i in self.data[category_name]['todo']:
            if i['id'] == todo_id:
                i['stat'] = True
                self.push_data()
                return 0

        return -2


class DotMD:
    def __init__(self, data: dict):
        self.data = data

    def _create_md_text(self):
        text = "# My TODO Lists\n\n"

        for category_name, v in self.data.items():
            text += f"## {category_name}\n"
            for todo in v['todo']:
                if todo['stat']:
                    text += "[X]"
                else:
                    text += "[ ]"

                text += f" {todo['text']}\n"

            text += "\n\n"

        now = datetime.datetime.now()
        text += f"Updated at {now.year}/{now.month}/{now.day} {now.hour}:{now.minute}"

        return text

    def update_md_file(self):
        text = self._create_md_text()
        with open('./todo.md', 'w') as File:
            File.write(text)

    def print_md_file(self):
        text = self._create_md_text()

        console = Console()
        md = Markdown(text)
        console.print(md)


def print_beautiful_todo(data):
    colors = ['blue', 'yellow', 'magenta', 'cyan',
              'bright_magenta', 'bright_cyan', 'deep_sky_blue3',
              'cyan1', 'medium_turquoise', 'light_slate_blue', 'pale_turquoise1',
              'khaki1']

    for category_name, v in data.items():
        table = Table(box=box.ROUNDED, expand=True)

        table.add_column(f"[{random.choice(colors)}]" + category_name, justify="center", style="cyan", no_wrap=True)

        for todo in v['todo']:
            if todo['stat']:
                table.add_row("[green]" + todo['text'])
            else:
                table.add_row("[red]" + todo['text'])

        console = Console()
        console.print(table)
