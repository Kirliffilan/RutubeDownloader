from database import init_database
from gui import App


def main():
    init_database()

    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()