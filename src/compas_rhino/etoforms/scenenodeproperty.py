from __future__ import print_function
from __future__ import absolute_import
from __future__ import division


import compas

try:
    import rhinoscriptsyntax as rs
    import scriptcontext as sc
    find_object = sc.doc.Objects.Find
    import System
    import Rhino.UI
    import Eto.Drawing as drawing
    import Eto.Forms as forms
except Exception:
    compas.raise_if_ironpython()


from compas_rhino.etoforms import PropertyListForm
from compas.datastructures import Mesh

__all__ = ['SceneNodePropertyForm']

class Tree_Table(forms.TreeGridView):
    def __init__(self, ShowHeader=True):
        self.ShowHeader = ShowHeader
        self.Height = 300

    @classmethod
    def from_sceneNode(cls, sceneNode):
        table = cls(ShowHeader=False)
        table.add_column()
        table.add_column()

        treecollection = forms.TreeGridItemCollection()
        treecollection.Add(forms.TreeGridItem(Values=('Type', sceneNode.item.__class__.__name__)))
        treecollection.Add(forms.TreeGridItem(Values=('Name', sceneNode.artist.name)))
        treecollection.Add(forms.TreeGridItem(Values=('Layer', sceneNode.artist.layer)))

        if hasattr(sceneNode.artist, 'settings'):
            settings = forms.TreeGridItem(Values=('Settings',))
            treecollection.Add(settings)
            for key in sceneNode.artist.settings:
                settings.Children.Add(forms.TreeGridItem(Values=(key, str(sceneNode.artist.settings[key]))))
    
        table.DataStore = treecollection
        return table

    @classmethod
    def from_vertices(cls, sceneNode):

        mesh = sceneNode.item
        table = cls()
        table.add_column('key')
        table.add_column('x')
        table.add_column('y')
        table.add_column('z')
        treecollection = forms.TreeGridItemCollection()
        for key in mesh.vertices():
            treecollection.Add(forms.TreeGridItem(Values=(key, mesh.vertex[key]['x'], mesh.vertex[key]['y'], mesh.vertex[key]['z'])))
        table.DataStore = treecollection
        table.CellClick += table.SelectEvent(sceneNode.artist.vertices)
        return table

    @classmethod
    def from_edges(cls, sceneNode):
        mesh = sceneNode.item
        table = cls()
        table.add_column('key')
        table.add_column('vertices')
        table.add_column('x')
        table.add_column('y')
        table.add_column('z')
        treecollection = forms.TreeGridItemCollection()
        for key, edge in enumerate(mesh.edges()):
            edge_item = forms.TreeGridItem(Values=(key, str(edge)))
            treecollection.Add(edge_item)
            for key in edge:
                vertex_item = forms.TreeGridItem(Values=('', key, mesh.vertex[key]['x'], mesh.vertex[key]['y'], mesh.vertex[key]['z']))
                edge_item.Children.Add(vertex_item)
        table.DataStore = treecollection
        table.CellClick += table.SelectEvent(sceneNode.artist.edges, sceneNode.artist.vertices)
        return table

    @classmethod
    def from_faces(cls, sceneNode):
        mesh = sceneNode.item
        table = cls()
        table.add_column('key')
        table.add_column('vertices')
        table.add_column('x')
        table.add_column('y')
        table.add_column('z')
        treecollection = forms.TreeGridItemCollection()
        for key in mesh.faces():
            face_item = forms.TreeGridItem(Values=(key, str(mesh.face[key])))
            treecollection.Add(face_item)
            for v in mesh.face[key]:
                vertex_item = forms.TreeGridItem(Values=('', v, mesh.vertex[v]['x'], mesh.vertex[v]['y'], mesh.vertex[v]['z']))
                face_item.Children.Add(vertex_item)
        table.DataStore = treecollection
        table.CellClick += table.SelectEvent(sceneNode.artist.faces, sceneNode.artist.vertices)
        return table

    def SelectEvent(self, GUIDs, GUIDs2=None):
        def on_selected(sender, event):
            try:
                rs.UnselectAllObjects()
                key = event.Item.Values[0]
                if key != '':
                    find_object(GUIDs[key]).Select(True)
                else:
                    key = event.Item.Values[1]
                    find_object(GUIDs2[key]).Select(True)
            except Exception as e:
                print(e)
        
        return on_selected

    def add_column(self, HeaderText=None, Editable=False):
        column = forms.GridColumn()
        if self.ShowHeader:
            column.HeaderText = HeaderText
        column.Editable = Editable
        column.DataCell = forms.TextBoxCell(self.Columns.Count)
        self.Columns.Add(column)


class SceneNodePropertyForm(forms.Form):

    def setup(self, sceneNode):
        self.Rnd = System.Random()
        self.Title = "Properties"
        self.TabControl = self.from_sceneNode(sceneNode)
        tab_items = forms.StackLayoutItem(self.TabControl, True)
        layout = forms.StackLayout()
        layout.Spacing = 5
        layout.HorizontalContentAlignment = forms.HorizontalAlignment.Stretch
        layout.Items.Add(tab_items)
        self.Content = layout
        self.Padding = drawing.Padding(12)
        self.Resizable = False
        self.ClientSize = drawing.Size(400, 600)

    def from_sceneNode(self, sceneNode):
        control = forms.TabControl()
        control.TabPosition = forms.DockPosition.Top

        tab = forms.TabPage()
        tab.Text = "Basic"
        tab.Content = Tree_Table.from_sceneNode(sceneNode)
        control.Pages.Add(tab)

        if isinstance(sceneNode.item, Mesh):
            tab = forms.TabPage()
            tab.Text = "Vertices"
            tab.Content = Tree_Table.from_vertices(sceneNode)
            control.Pages.Add(tab)

            tab = forms.TabPage()
            tab.Text = "Edges"
            tab.Content = Tree_Table.from_edges(sceneNode)
            control.Pages.Add(tab)

            tab = forms.TabPage()
            tab.Text = "Faces"
            tab.Content = Tree_Table.from_faces(sceneNode)
            control.Pages.Add(tab)

        return control


if __name__ == "__main__":

    from compas_rhino.scene import Scene

    scene = Scene()

    mesh = Mesh.from_polyhedron(6)

    node = scene.add(mesh, name="Cube", layer="World")
    
    scene.update()

    dialog = SceneNodePropertyForm()
    dialog.setup(node)
    dialog.Show()