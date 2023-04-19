#pragma once

#include <map>
#include <list>
#include <vector>

class Graph
{
public:
  Graph() = default;

  void addEdge(int const start, int const finish)
  {
    edges.push_back({start, finish});
  }

  void addVertex(int const index, int const label)
  {
    auto const & it = vertexLabels.find(index);
    if (it == vertexLabels.cend())
    {
      vertexLabels.insert({index, label});
    }
  }

  std::list<std::vector<int>> const * getEdges() const
  {
    return &this->edges;
  }

  std::map<int, int> const * getVertexLabels() const
  {
    return &this->vertexLabels;
  }

private:
  std::map<int, int> vertexLabels;
  std::list<std::vector<int>> edges;
};
