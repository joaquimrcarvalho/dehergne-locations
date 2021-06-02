""" timelink.py
Interface to timelink/MHK databases.

Joaquim Carvalho, Macau, 2021.
MIT License.
"""
from sqlalchemy import create_engine,text
from itertools import combinations
from sqlalchemy.orm import Session
import networkx as nx

def network_from_attribute(engine,attribute: str, mode='cliques'):
    """ Generate a network from common attribute values

    Args:   
        engine: a sqlalchemy engine
        attribute (str): the type of attribute
    
    Returns:
        a networkx Graph object (networkx.classes.graph.Graph)

    This function will generate a network connecting the
    entities that have the same value for the 
    attribute given in the parameter.

    The network will have as Edge Attributes
    - attribute: the name of the attribute given in the parameter
    - value: the value common to the two nodes
    - date1,date2: the dates of the attribute in each node.

    """

    sql = "select distinct the_value from attributes where the_type = :the_type and the_value <> '?'"
    G = nx.Graph()
    with engine.connect() as conn:
        result = conn.execute(text(sql),[{'the_type':attribute}])
        values= result.all()
        for (avalue,) in values:
            sql = "select entity,the_date from attributes where the_type=:the_type and the_value = :the_value"
            result = conn.execute(text(sql),[{'the_type':attribute,'the_value':avalue}])
            entities = result.all()
            if (len(entities)>1):
                pairs = list(combinations(entities,2))
                # TODO: optional date range filtering
                for ((e1,d1),(e2,d2)) in pairs:
                    G.add_edges_from([(e1,e2,{'date1':d1,'date2':d2,'attribute':attribute,'value':avalue})])     
    return G