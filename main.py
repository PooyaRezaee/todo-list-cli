import os
from simple_term_menu import TerminalMenu
from utils import RWData, DotMD, print_beautiful_todo
from rich import print
from rich.panel import Panel
from rich.text import Text


class Pages:
    def __init__(self, rw_data: RWData):
        self.rw_data = rw_data
        self.rw_data.pull_data()

        self.start_options = ["Show Todo", "Change Todo",  "Update to .md file", "Reset", '', "Exit"]

        self.selected_item = {'category': None, "todo": None}
        self.flash_message = ''

        self.DONE = "Done"
        self.DELETE = 'Delete'
        self.BACK = "Back"
        self.ADD = "Add"

    @staticmethod
    def _new_page(text="***", color='bright_cyan', subtitle=''):
        os.system('clear')
        print(Panel(Text(text, justify='center', style=f"bold {color}"), subtitle=subtitle))
        # print(Panel(f"[{color}]{title}",title_align='center'))

    @staticmethod
    def _terminal_menu(options):
        return TerminalMenu(options,
                            menu_cursor='  ',
                            cycle_cursor=True,
                            menu_cursor_style=('bg_blue', 'fg_black'),
                            menu_highlight_style=('bg_black', 'fg_green', 'bold'),
                            skip_empty_entries=True,
                            )

    def _todo_options(self, is_done=False):
        if is_done:
            return [self.DELETE, self.BACK]
        else:
            return [self.DONE, self.DELETE, self.BACK]

    def _category_options(self):
        category_list = self.rw_data.category_list()

        if len(category_list) > 0:
            category_list.append("")
        category_list.append(self.ADD)
        category_list.append(self.BACK)
        return category_list

    def _list_todo_options(self, category_name):
        todo_list = self.rw_data.todo_list(category_name)

        humanize_todo_list = []
        for i in todo_list:
            if i['stat']:
                humanize_todo_list.append(
                    f"[X] {i['text']}"
                )
            else:
                humanize_todo_list.append(
                    f"[ ] {i['text']}"
                )

        if len(humanize_todo_list) > 0:
            humanize_todo_list.append("")

        humanize_todo_list.append(self.ADD)
        humanize_todo_list.append(self.DELETE)
        humanize_todo_list.append(self.BACK)

        return humanize_todo_list, todo_list

    def _category_page(self):
        # self._new_page("Categories", subtitle="[red]ctrl-d For Delete [white]| [green]ctrl-a for add")
        # TODO Use accept-key for future

        self._new_page("Categories")

        category_list = self._category_options()
        category_menu = self._terminal_menu(category_list)
        category_entry_index = category_menu.show()

        if category_entry_index is None:
            return None

        category_name = category_list[category_entry_index]

        if category_name == self.BACK:
            return None
        elif category_name == self.ADD:
            self._new_page("Enter Category Name")
            category_name = input(">> ")
            self.rw_data.add_category(category_name)
            self.flash_message += f'- [green]Added category {category_name}\n'
            return False

        self.selected_item['category'] = category_name
        return category_name

    def _todo_page(self, category_name):
        while True:
            self._new_page(f"Todo {category_name}")

            humanize_todo_list, todo_list = self._list_todo_options(category_name)
            todo_menu = self._terminal_menu(humanize_todo_list)
            todo_entry_index = todo_menu.show()

            if todo_entry_index is None:
                return None

            humanize_entry_text = humanize_todo_list[todo_entry_index]

            if humanize_entry_text == self.BACK:
                return None
            elif humanize_entry_text == self.ADD:
                self._new_page("Enter Todo Text")
                todo_text = input(">> ")
                self.rw_data.todo_add(category_name, todo_text)
                self.flash_message += f'- [green]Added New Todo\n'

                return False
            elif humanize_entry_text == self.DELETE:
                self._new_page("Are You Sure?", color='red')
                entry_sure = self._terminal_menu(['No', 'Yes']).show()

                if entry_sure:
                    self.rw_data.remove_category(category_name)
                    self.flash_message += f'- [green]Category {category_name} deleted\n'

                return None
            todo = todo_list[todo_entry_index]

            self.selected_item['todo'] = todo['id']
            return {"status": todo['stat']}

    def _todo_change_page(self, status_todo):
        category_name = self.selected_item['category']
        todo_id = self.selected_item['todo']

        self._new_page(f"What do want do on {category_name}-{todo_id}")

        todo_options = self._todo_options(status_todo)
        choice_todo_menu = self._terminal_menu(todo_options)
        choice_todo_entry_index = choice_todo_menu.show()

        if choice_todo_entry_index is None:
            return None

        match todo_options[choice_todo_entry_index]:
            case "Done":
                self.rw_data.todo_done(category_name, todo_id)
                self.flash_message += f'- [green]Done todo in {category_name}\n'
                return 1
            case "Delete":
                self.rw_data.todo_remove(category_name, todo_id)
                self.flash_message += f'- [green]todo {category_name}-{todo_id} deleted\n'
                return 2
            case self.BACK:
                return None

    def start(self):
        while True:
            self._new_page("Choice a option")
            print(self.flash_message)
            self.flash_message = ''

            start_menu = self._terminal_menu(self.start_options)
            menu_entry_index = start_menu.show()

            if menu_entry_index is None:
                break

            match self.start_options[menu_entry_index]:
                case "Change Todo":
                    while True:
                        category = self._category_page()
                        if category is None:
                            break
                        elif not category:
                            continue

                        while True:
                            status_todo = self._todo_page(category)
                            if status_todo is None:
                                break
                            if not status_todo:
                                continue

                            selected = self._todo_change_page(status_todo['status'])
                            if selected:
                                continue
                            else:
                                break
                case "Show Todo":
                    os.system('clear')
                    print_beautiful_todo(self.rw_data.data)
                    input("Press Key for return to menu ...")
                    continue
                case "Update to .md file":
                    dmd = DotMD(self.rw_data.data)
                    dmd.update_md_file()
                    print("todo.md File Updated.")
                    see = input("Do you want see It?(Y/n)")
                    if see.lower() == 'y' or see == '':
                        dmd.print_md_file()
                        input("Press key for return to menu ...")
                    self.flash_message = '[green]updated todo.md.'
                    continue
                case "Reset":
                    with open('./data.json', 'r') as File:
                        with open("./data-backup.json", 'w') as FileBackup:
                            FileBackup.write(File.read())

                    with open('./data.json', 'w') as File:
                        File.write('{}')
                        self.flash_message = "[yellow]The data was reset!\n(exist backup in data-backup.json)"
                case "Exit":
                    self._new_page("Good Bye", color='cyan')
                    break
                case _:
                    self.flash_message = "[red]Invalid Parameter"
                    continue


def main():
    rw_data = RWData()
    pages = Pages(rw_data)

    pages.start()


main()
