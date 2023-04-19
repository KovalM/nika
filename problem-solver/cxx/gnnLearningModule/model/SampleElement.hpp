#pragma once

#include <utility>

#include "Graph.hpp"

class SampleElement
{
public:
  SampleElement() = default;

  SampleElement(Graph * graph, int const classIndex) : graph(graph), classIndex(classIndex){}

  [[nodiscard]] Graph const * getGraph() const
  {
    return this->graph;
  }

  [[nodiscard]] int getClassIndex() const
  {
    return classIndex;
  }

private:
  Graph * graph;
  int classIndex;
};

