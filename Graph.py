class Vertex:

    def __init__(self, key, payload=None):
        self._key = key
        self._payload = payload

    def get_key(self):
        return self._key

    def get_info(self):
        return self._payload

    def __hash__(self):
        return hash(self.get_key())


class Edge:

    def __init__(self, start, end, weight=None):
        self._start = start
        self._end = end
        self._weight = weight

    def get_vs(self):
        return self._start, self._end

    def get_info(self):
        return self._weight

    def opposite(self, v):      
        if v == self._start:
            return self._end
        else:
            return self._start

    def __hash__(self):
        return hash(self.get_vs())


class Graph:

    def __init__(self):     
        self._graph = {}    
        self._vertex = 0    
        self._edge = 0     

    def add_vertex(self, key, payload=None):
        if key not in self._graph.keys():
            vertex = Vertex(key, payload)           
            self._graph[vertex.get_key()] = []      
            self._vertex = self._vertex + 1

    def vertex_count(self):
        return self._vertex

    def add_edge(self, start, end, payload=None, weight=None):
        if start not in self._graph.keys():          
            self.add_vertex(start, payload)
        if end not in self._graph.keys():            
            self.add_vertex(end, payload)

        edge = Edge(start, end, weight)              
        self._graph[start].append(edge)              
        self._graph[end].append(edge)                
        self._edge = self._edge + 1

    def edge_count(self):
        return self._edge

    def degree(self, vertex):
        if vertex in self._graph.keys():            
            values = self._graph[vertex]            
            return len(values)                      
        else:
            raise ValueError('The vertex is not on this graph')

    def remove_edge(self, v1, v2):
        v1_list = self._graph[v1]                  
        v2_list = self._graph[v2]                  
        for i in v1_list:
            for j in v2_list:
                if str(i) == str(j):               
                    self._graph[v1] .remove(i)     
                    self._graph[v2] .remove(j)    

    def remove_vertex(self, v1):
        v1_list = self._graph[v1]                  
        v1_vertexs = []                            
        for i in v1_list:
            v1_vertexs.append(i.opposite(v1))     
        for i in v1_vertexs:                       
            arestas = self._graph[i]
            for j in arestas:                      
                if j.opposite(i) == v1:            
                    self._graph[i].remove(j)      
                    self._edge = self._edge - 1
        del self._graph[v1]                        
        self._vertex = self._vertex - 1

    def _iter_vertex(self):
        return self._graph.keys()

    def _iter_edges(self):
        return self._graph.values()