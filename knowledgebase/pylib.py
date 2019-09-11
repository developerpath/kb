#CUSTOM FUNCTIONS (will be separated when grow)
from django.urls import reverse_lazy

#Recreate to function that return sidebar and orphaned items as separate list
#(orphaned items do not show up)
class Sidebar():
    def __init__(self, data, function):
        self.data = data,
        self.itm_has_child = [child.page_parent_id_id for child in data if child.page_parent_id_id]
        self.pid_ls = [page.id for page in data]
        self.orphaned = [page for page in data if page.page_parent_id_id not in self.pid_ls]
        self.func = function
        self.active = True
        self.itm_fmt = """<LI {}><a href="{}">{}</a></LI>{}""".format
        self.output = ''
        
    def mksidebar(self, parent_id, idx, init=True):
        ls = ['<UL>']
        css_class_fmt = 'class="{}"'.format

        for itm in self.data[0]:
            if itm.page_parent_id_id == parent_id:
                url = reverse_lazy(self.func,
                    kwargs = {
                        'space_id':itm.space_id_id,
                        'page_id':itm.id,
                })

                if self.active:
                    if itm.id in self.itm_has_child:
                        css_class = css_class_fmt('tree-arrow-down active')
                    else:
                        css_class = css_class_fmt('active')
                elif itm.id in self.itm_has_child:
                    if itm.page_parent_id_id == parent_id:
                        css_class = css_class_fmt('tree-arrow-down')
                    else:
                        css_class = css_class_fmt('tree-arrow')
                else: css_class = ''
                
                if itm.id == idx and not init:
                    ls.append(self.itm_fmt(css_class, url, itm.page_title, '{}'))
                    self.active = False
                else:
                    if itm.id in self.itm_has_child:
                        css_class = css_class_fmt('tree-arrow')
                    else:
                        css_class = ''
                    ls.append(self.itm_fmt(css_class, url, itm.page_title, ''))

        ls.append('</UL>')
        parent_idx = [child for child in self.data[0] if child.id == parent_id]

        if len(ls) <= 2: ls = ['']
        if parent_idx:
            self.output = ''.join(ls).format(self.output)
            return self.mksidebar(parent_idx[0].page_parent_id_id, parent_idx[0].id, init=False)
        else:
            return ''.join(ls).format(self.output)