import streamlit as st
from streamlit_antd_components import menu, MenuItem


# Controller
class PageController:
    def __init__(self, view):
        self.view = view

    def handle_navigation(self, pages):
        if 'page' not in st.session_state:
            st.session_state.page = 'main'

        menu_items = [MenuItem(page.name, icon='app') for page in pages]
        with st.sidebar:
            st.session_state.page = menu(menu_items, format_func='title', open_all=True)

        selected_page = next((page for page in pages if page.name == st.session_state.page), None)
        if selected_page:
            self.view.show_page(selected_page)


# Model
class PageModel:
    def __init__(self, name, title, content):
        self.name = name
        self.title = title
        self.content = content


# View
class PageView:
    def show_page(self, model):
        st.title(model.title)
        for widget in model.content:
            widget()


# Define the content of the pages
home_content = [lambda: st.write("欢迎来到主页！")]
detail_content = [lambda: st.write("这是详细信息页面。")]

# Create the pages
home_page = PageModel("main", "主页", home_content)
detail_page = PageModel("detail", "详细信息", detail_content)

# Create the view and the controller
view = PageView()
controller = PageController(view)


# Run the app
def main():
    controller.handle_navigation([home_page, detail_page])


if __name__ == "__main__":
    main()
