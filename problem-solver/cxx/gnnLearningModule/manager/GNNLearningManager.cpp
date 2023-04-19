#include <map>

#include "sc-agents-common/utils/CommonUtils.hpp"

#include "GNNLearningManager.hpp"
#include "model/SampleElement.hpp"

using namespace utils;

namespace gnnLearningModule
{
GNNLearningManager::GNNLearningManager(ScMemoryContext * context) : context(context)
{
  jsonFileTranslator = make_unique<SampleToJsonFileTranslator>();
}

ScAddrVector GNNLearningManager::manage(ScAddrVector const & processParameters)
{
  size_t classesNumber = processParameters.size();

  std::list<SampleElement *> trainSample;
  std::list<SampleElement *> testSample;
  double averageVertexesSize = 0;
  double averageEdgesSize = 0;
  for (int classIndex = 0; classIndex < classesNumber; classIndex++)
  {
    ScAddr currentClass = processParameters[classIndex];
    int classElementsNumber = std::min(
        utils::CommonUtils::getPowerOfSet(context, currentClass),
        100);
    int trainSampleSize = (int)(classElementsNumber * 0.8);

    SC_LOG_INFO("GNNLearningManager: Process class " + std::to_string(classIndex) + " with " + std::to_string(classElementsNumber) + " elements");

    int index = 0;
    ScIterator3Ptr iterator3 = context->Iterator3(
        currentClass,
        ScType::EdgeAccessConstPosPerm,
        ScType::Unknown);
    while (iterator3->Next())
    {
      auto graph = translateSemanticNeighborhood(iterator3->Get(2));
      averageVertexesSize += (double)graph->getVertexLabels()->size();
      averageEdgesSize += (double)graph->getEdges()->size();
      auto sample = new SampleElement(graph, classIndex);
      if (index <= trainSampleSize)
      {
        trainSample.push_back(sample);
      }
      else
      {
        testSample.push_back(sample);
      }
      index++;
      if (index > classElementsNumber)
      {
        break;
      }
    }
  }

  jsonFileTranslator->translate(trainSample, SAMPLE_PATH + "/train/");
  jsonFileTranslator->translate(testSample, SAMPLE_PATH + "/test/");

  averageVertexesSize = averageVertexesSize / (double)(trainSample.size() + testSample.size());
  averageEdgesSize = averageEdgesSize / (double)(trainSample.size() + testSample.size());

  SC_LOG_INFO("Train sample size: " + std::to_string(trainSample.size()));
  SC_LOG_INFO("Test sample size: " + std::to_string(testSample.size()));
  SC_LOG_INFO("Average graph. Vertexes: "
              + std::to_string(averageVertexesSize)
              + "Edges: " + std::to_string(averageEdgesSize));

  return {};
}

Graph * GNNLearningManager::translateSemanticNeighborhood(ScAddr const & element)
{
  auto graph = new Graph();
  translatedScElements.clear();

  if (context->GetElementType(element).IsEdge())
  {
    translateEdge(element, graph);
  }
  else
  {
    resolveElementInTranslation(element, graph);
    translateClasses(element, graph);
  }

  return graph;
}

int GNNLearningManager::resolveElementInTranslation(ScAddr const & element, Graph * graph)
{
  auto const & it = translatedScElements.find(element);
  if (it != translatedScElements.cend())
  {
    return it->second;
  }
  else
  {
    int vertexIndex = translatedScElements.size();
    translatedScElements.insert({element, vertexIndex});

    int vertexLabel = getVertexLabel(element);
    graph->addVertex(vertexIndex, vertexLabel);
    return vertexIndex;
  }
}

int GNNLearningManager::getVertexLabel(ScAddr const & element)
{
  int label = -1;
  ScType type = context->GetElementType(element);
  for (int i = 0; i < usedTypes.size(); i++)
  {
    if (type == usedTypes[i])
    {
      label = i;
      break;
    }
  }
  if (label < 0)
  {
    label = (int) usedTypes.size();
    usedTypes.push_back(type);
  }
  return label;
}

void GNNLearningManager::translateEdge(ScAddr const & edge, Graph * graph)
{
  ScAddr start = context->GetEdgeSource(edge);
  int startIndex = resolveElementInTranslation(start, graph);

  int edgeIndex = resolveElementInTranslation(edge, graph);

  ScAddr finish = context->GetEdgeTarget(edge);
  int finishIndex = resolveElementInTranslation(finish, graph);

  graph->addEdge(startIndex, edgeIndex);
  graph->addEdge(edgeIndex, finishIndex);

  translateClasses(start, graph);
  translateClasses(edge, graph);
  translateClasses(finish, graph);
}

void GNNLearningManager::translateClasses(ScAddr const & element, Graph * graph)
{
  int elementIndex = resolveElementInTranslation(element, graph);
  ScIterator3Ptr iterator3 = context->Iterator3(
      ScType::Node,
      ScType::EdgeAccessConstPosPerm,
      element);
  while (iterator3 -> Next())
  {
    ScAddr start = iterator3->Get(0);
    int startIndex = resolveElementInTranslation(start, graph);

    ScAddr scArc = iterator3->Get(1);
    int arcIndex = resolveElementInTranslation(scArc, graph);

    graph->addEdge(startIndex, arcIndex);
    graph->addEdge(arcIndex, elementIndex);
    translateClasses(scArc, graph);
  }
}

void GNNLearningManager::translateRoleRelations(ScAddr const & element, Graph * graph)
{
  // TODO
}

void GNNLearningManager::translateNoRoleRelations(ScAddr const & element, Graph * graph)
{
  // TODO
}
}