#include <unordered_map>

#include "sc-memory/sc_memory.hpp"

#include "model/Graph.hpp"
#include "translator/SampleToJsonFileTranslator.hpp"

namespace gnnLearningModule
{
class GNNLearningManager
{
private:
  std::string const SAMPLE_PATH = "/home/mkovalev/Documents/research/projects/nika/sample";

public:
  explicit GNNLearningManager(ScMemoryContext * context);

  ScAddrVector manage(ScAddrVector const & processParameters);

  Graph * translateSemanticNeighborhood(ScAddr const & element);

private:
  void translateEdge(ScAddr const & edge, Graph * graph);

  void translateClasses(ScAddr const & element, Graph * graph);

  void translateRoleRelations(ScAddr const & element, Graph * graph);

  void translateNoRoleRelations(ScAddr const & element, Graph * graph);

  int resolveElementInTranslation(ScAddr const & element, Graph * graph);

  int getVertexLabel(ScAddr const & element);

  ScMemoryContext * context;
  unique_ptr<SampleToJsonFileTranslator> jsonFileTranslator;
  std::unordered_map<ScAddr, int, ScAddrHashFunc<size_t>, ScAddrLessFunc> translatedScElements;
  std::vector<ScType> usedTypes;
};

}
