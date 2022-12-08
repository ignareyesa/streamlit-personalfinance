import streamlit as st  
from st_click_detector import click_detector
from streamlit_extras.switch_page_button import switch_page

def load_css_file(css_file_path, as_markdown = True):
    with open(css_file_path) as f:
        if as_markdown:
            return st.markdown(f"<style>{f.read()}</style>",
                            unsafe_allow_html=True)
        else:
            return f"<style>{f.read()}</style>"

# determine is user is logged_in or nor
def logged_in(session_state = st.session_state):
    try:
        if session_state["authentication_status"]:
            return True
    except KeyError:
        st.session_state['authentication_status'] = None 
        st.session_state['username'] = ''
        st.session_state['logout'] = None
        st.session_state['name'] = None
        st.session_state['init'] = None

def multiple_buttons(labels:list, links, html_class:str="css-1x8cf1d edgvbvh10", css:str="styles/default_buttons.css"):
    if len(labels)==len(links):
        content = load_css_file(css, as_markdown=False)
        for i,label in enumerate(labels):
            temp_content = f"""<a href="" id="link_{i}" class="{html_class}">{label}</a> """
            content+=temp_content
        clicked = click_detector(content)
        for i, link in enumerate(links):
            if clicked==f"link_{i}":
                switch_page(link)
        return content
    else:
        raise Exception("labels and links length must have the same lenght")