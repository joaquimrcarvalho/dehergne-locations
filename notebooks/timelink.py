""" timelink.py
Interface to timelink/MHK databases.

TODO get_community(dbname) gets content of mhk_env and returns a community object with the sqlAlchemy incorporated
TODO 

Joaquim Carvalho, Macau, 2021.
MIT License.
"""
from sqlalchemy import create_engine,text
import os
from dotenv import dotenv_values
from itertools import combinations
from sqlalchemy.orm import Session
import networkx as nx
from sqlalchemy import create_engine,text


class Community:
    """
    Interface to a Timelink/MHK community

    TODO get_community(dbname) gets content of mhk_env and returns a community object with the sqlAlchemy incorporated
    TODO db_stats Returns the db status
    TODO sources = a list of sources from the sources tables
    TODO events = a list of acts and events.
    """
    pass
 
    
def get_dbnames():
    result = []
    app_env = get_mhk_app_env()
    pwd = app_env['MYSQL_ROOT_PASSWORD']  
    connection_string = "mysql+mysqlconnector://root:{pwd}@localhost:3307/mysql".format(pwd=pwd)
    mysql = create_engine(connection_string,echo=False,future=True)
    with mysql.connect() as conn:
        databases = conn.execute(text("SELECT table_schema FROM information_schema.tables WHERE  table_name = 'entities'"))
        result = [db[0] for db in databases]
    return result

def get_mhk_env():
    result = {}
    home_dir=os.getenv('HOME')
    print("home  : "+home_dir)
    result = dotenv_values(home_dir+"/.mhk")
    return result

def get_mhk_app_env():
    mhk_env=get_mhk_env()
    mhk_home_dir=mhk_env['HOST_MHK_HOME']
    app_env = dotenv_values(mhk_home_dir+'/app/.env')
    return app_env


def network_from_attribute(e,a: str, mode='cliques',user="*none*"):
    """Generate a network from common attribute values.

    This function will generate a network connecting the
    entities that have the same value for the 
    attribute given in the parameter.
    
    Parameters
    ----------
    e : sqlalchemy Engine
        An SQLAlchemy engine connected to the target database.
    a : str
        The name (type) of the attribute used for generating the graph.
    user: str  use real persons identified by this user (optional).
    mode : {"cliques", "value-node"}, optional (default="cliques")
        The topology the generated network.
        
        If mode = "cliques" all the entities with attribute `a` will be 
        nodes in the graph and edges will be created between the entities with the same
        value of the attribute.

        If mode = "value-node" a node will be created for each different
        value of the attribute `a` and edges will be created linking that node
        to the entities which have that value in attribute `a`.
        In both cases entities with several values for the attribute contribute to the 
        overall connectivity of the graph, by linking clusters of same value entities.

    Returns
    -------
    networkx Graph (networkx.classes.graph.Graph)
        Each node will have an associated dictionary of attributes 
            "id" (entity id) 
            "type" "value_node" or entity class in the database.
            "desc" a description of the node, automatically fetched
                from the database (names of persons for instance)
            "is_real" a flag stating if the "id" key refers to a real 
            entity or to an occurrence.
            "url" a link to the entity information in the database
                inf the format http://localhost:8080/mhk/database/id/entityID
        Each edge will have associated the following key-value pairs
            "date1" date of the atribute in the left most node
            "date2" date of the attribute in the right most node
            "attribute" the type of the attribute
            "value" the value of the attribute 

    Examples
    --------

        G = network_from_attribute(e, "graduated_at", mode="value-node")

    """

    sql = "select distinct the_value from attributes where the_type = :the_type and the_value <> '?'"
    G = nx.Graph()
    with e.connect() as conn:
        result = conn.execute(text(sql),[{'the_type':a}])
        values= result.all()
        for (avalue,) in values:
            if (user == "*none*"):
                sql = "select id,name,the_date from nattributes where the_type=:the_type and the_value = :the_value"
            else:
                sql = "SELECT IFNULL( (select rid from rlinks where instance=n.id and user=:user),id) as id, name, the_date  from nattributes n where the_type=:the_type and the_value = :the_value"
            ## TODO also fetch the instance SELECT IFNULL( (select rid from rlinks where instance=n.id and user=:user),id) as id, id as instance, name,...
            ## TODO then test if id=instance. If not add attribute to node is_real=yes otherwise "no"
            ## TODO do the same with the first select.
            ## TODO add to nodes a url attribute if host and dbase are present is present https://joaquims-mbpr.local/mhk/toliveira/id/rp-1
            result = conn.execute(text(sql),[{'the_type':a,'the_value':avalue,'user':user}])
            entities = result.all()
                    
            if (mode=="value-node"):
                G.add_node(avalue,desc=avalue,type=a)
                for (id,name,date) in entities:
                    G.add_node(id,desc=name,type='person')
                    G.add_edge(avalue,id,date1 = date, date2 = date,attribute=a, value=avalue)
            elif (len(entities)>1):
                for (id,name,date) in entities:
                    G.add_node(id,desc=name,type='person') # this should come from the entity class
                pairs = list(combinations(entities,2))
                # TODO: optional date range filtering
                for ((e1,n1,d1),(e2,n1,d2)) in pairs:
                    G.add_edges_from([(e1,e2,{'date1':d1,'date2':d2,'attribute':a,'value':avalue})]) 
    return G

from bokeh.models import Range1d, Circle, ColumnDataSource, MultiLine, NodesAndLinkedEdges,EdgesAndLinkedNodes
from bokeh.plotting import figure
from bokeh.plotting import from_networkx
from bokeh.palettes import Spectral4
from bokeh.io import show, save
import networkx as nx

def draw_network(G,
        title='Timelink network',
        hover_tooltips=[("desc","@desc"),("type","@type")],
        iterations=50,
        node_colors=('type', # TODO this should be generic maybe bokeh has builtin
                    {'person':'green',
                    'wicky-viagem':'red',
                    'jesuita-entrada':'blue',
                    '*default*':'gray'}),
        width=500,height=500):

    """ draws a network using Bokeh and networkx layout

    """   
   
    #Establish which categories will appear when hovering over each node
    HOVER_TOOLTIPS = hover_tooltips

    # Color nodes
    (cattribute, node_colors) = node_colors
    for m in list(G.nodes):
        nt = G.nodes[m].get(cattribute,"*default*")
        nc = node_colors.get(nt,'gray')
        G.nodes[m]['color'] = nc

    #Create a plot — set dimensions, toolbar, and title
    plot = figure(tooltips = HOVER_TOOLTIPS,
                tools="pan,wheel_zoom,save,reset", active_scroll='wheel_zoom',
                x_range=Range1d(-20.1, 20.1), y_range=Range1d(-15.1, 15.1), plot_width=width,plot_height=height,title=title)

    #Create a network graph object with spring layout
    # https://networkx.github.io/documentation/networkx-1.9/reference/generated/networkx.drawing.layout.spring_layout.html
    network_graph = from_networkx(G, nx.spring_layout, iterations=iterations,scale=20, center=(0, 0))


    #Set node size and color
    network_graph.node_renderer.glyph = Circle(size=15, fill_color='color')

    #Set edge opacity and width
    network_graph.edge_renderer.glyph = MultiLine(line_alpha=0.5, line_width=1)

    #Add network graph to the plot
    plot.renderers.append(network_graph)
    show(plot)
    fn = save(plot, title=title, filename=f"{title}.html") 
    print("timelink draw_network plot saved to file: "+fn)

