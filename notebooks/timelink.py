""" timelink.py
Interface to timelink/MHK databases.

Joaquim Carvalho, Macau, 2021.
MIT License.
"""
from sqlalchemy import create_engine,text
from itertools import combinations
from sqlalchemy.orm import Session
import networkx as nx

def network_from_attribute(e,a: str, mode='cliques'):
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
            "is_rel" a flag stating if the "id" key refers to a real 
            entity or to an occurrence.
            "url" a link to the entity information in the database
                inf the format http://localhost:8080/mhk/database/id/entityID
        Each edge will have associated the following key-value pairs
            "date1" date of the atribute in the left most node
            "date2" date of the attribute in the right most node

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
            sql = "select id,name,the_date from nattributes where the_type=:the_type and the_value = :the_value"
            result = conn.execute(text(sql),[{'the_type':a,'the_value':avalue}])
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