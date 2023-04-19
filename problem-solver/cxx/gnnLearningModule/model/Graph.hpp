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
    std::string key = std::to_string(index);
    auto const & it = vertexLabels.find(key);
    if (it == vertexLabels.cend())
    {
      vertexLabels.insert({key, std::to_string(label)});
    }
  }

  std::list<std::vector<int>> const * getEdges() const
  {
    return &this->edges;
  }

  std::map<std::string, std::string> const * getVertexLabels() const
  {
    return &this->vertexLabels;
  }

private:
  std::map<std::string, std::string> vertexLabels;
  std::list<std::vector<int>> edges;
};
