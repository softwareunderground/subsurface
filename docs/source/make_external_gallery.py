"""
Modified after https://github.com/pyvista/pyvista/blob/ab70c26edbcfb107286c827bd4914562056219fb/docs/make_external_gallery.py

A helper script to generate the external examples gallery"""
import os


def format_icon(title, description, link, image):
    body = r"""
.. raw:: html

    <div class="sphx-glr-thumbcontainer" tooltip="{}">
    
.. only:: html

    .. figure:: {}
       :target: {}
       
       {}
       
       
       
       
       
       
.. raw:: html

    </div>
    
    
    
.. toctree::
   :hidden:
   
   
   {} <{}>
   
   
   
"""
    content = body.format(description, image, link, title, title, link)
    return content


class Example():
    def __init__(self, title, description, link, image):
        self.title = title
        self.description = description
        self.link = link
        self.image = image

    def format(self):
        return format_icon(self.title, self.description, self.link, self.image)


###############################################################################

articles = dict(
    gempy_well=Example(title="GemPy - Subsurface Link",
        description="Build a model from Subsurface object and export result back to subsurface",
        link="https://docs.gempy.org/integrations/gempy_subsurface.html#sphx-glr-integrations-gempy-subsurface-py",
        image="https://docs.gempy.org/_images/sphx_glr_gempy_subsurface_002.png"),
    segysag=Example(title="Using segysak with subsurface",
            description="Loading a segy cube into `subsurface.StructuredData`.",
            link="https://segysak.readthedocs.io/en/latest/examples/example_subsurface.html",
            image="https://raw.githubusercontent.com/trhallam/segysak/main/docs/_static/logo_small.png")

    # entry=Example(title="",
    #     description="",
    #     link="",
    #     image=""),
)


###############################################################################

def make_example_gallery():
    filename = "external/external_examples.rst"
    if os.path.exists(filename):
        os.remove(filename)
    with open(filename, "w") as f:
        f.write("""
External Examples
=================
Here are a list of longer, more technical examples of what PyVista can do!
.. caution::
    Please note that these examples link to external websites.
    If any of these links are broken, please raise an issue on the repository.
Do you have a technical processing workflow or visualization routine you
would like to share?
If so, please consider sharing your work here submitting a PR at
https://github.com/pyvista and we would be glad to add it!
""")
        # Reverse to put the latest items at the top
        for Example in list(articles.values())[::-1]:
            f.write(Example.format())

        f.write("""
.. raw:: html
    <div class="sphx-glr-clear"></div>
""")

    return