from pg_shared import LangstringsBase, Core

# Some central stuff which is used by both plain Flask and Dash views.

PLAYTHING_NAME = "hello-world"

class Langstrings(LangstringsBase):
    langstrings = {
        "HELLO_WORLD": {
            "en": "Hello World",
            "cy": "Helo Fyd"
        },
        "POP": {
            "en": "World Population",
            "cy": "Poblogaeth y Byd"
        },
        "YEARLY_CHANGE": {
            "en": "Yearly Change",
            "cy": "Newidiad Blynyddol"
        },
        "YEAR": {
            "en": "Year",
            "cy": "Blwyddyn"
        },
        "MENU_HELLO": {
            "en": "Hello",
            "cy": "Helo"
        },
        "MENU_ABOUT": {
            "en": "About",
            "cy": "Ynghylch"
        },
        "MENU_CHART": {
            "en": "Chart",
            "cy": "Siart"
        },
        "SHOW_LABEL": {
            "en": "Show:",
            "cy": "Sioe:"
        }
    }

# The menu is only shown if menu=1 in query-string AND only for specific views. Generally make the menu contain all views it is coded for
# Structure is view: LANGSTRING_KEY,
# - where "view" is the part after the optional plaything_root (and before <specification_id> if present) in the URL. e.g. "about" is a view.
# - and LANGSTRING_KEY is defined in the Langstrings class above
# The ROOT for a plaything is the index cards page and should not be in the menu.
# This defines the default order and the maximum scope of views in the meny. A plaything specification may override.
menu = {
    "hello": "MENU_HELLO",
    "chart": "MENU_CHART",
    "about": "MENU_ABOUT"
}

# This sets up core features such as logger, activity recording, core-config.
core = Core(PLAYTHING_NAME)