#include "sc-memory/utils/sc_log.hpp"

#include <fstream>
#include <filesystem>
#include <nlohmann/json.hpp>

#include "SampleToJsonFileTranslator.hpp"

namespace gnnLearningModule
{
bool SampleToJsonFileTranslator::translate(std::list<SampleElement *> const & sample, std::string const & path) const
{
  std::filesystem::remove_all(path);
  std::filesystem::create_directory(path);

  int index = 1;
  for (auto const & sampleElement : sample)
  {
    nlohmann::json elementJson;
    Graph const * graph = sampleElement->getGraph();

    elementJson[JSON_TARGET_KEY] = sampleElement->getClassIndex();
    elementJson[JSON_EDGES_KEY] = *(graph->getEdges());

    elementJson[JSON_LABELS_KEY] = *(graph->getVertexLabels());


    std::string filePath = path + std::to_string(index) + ".json";
    std::ofstream out;
    out.open(filePath, std::fstream::out);
    if (!out.is_open())
    {
      SC_LOG_ERROR("SampleToJsonFileTranslator: can't open file " + filePath);
      return false;
    }
    out << elementJson;
    out.close();

    index++;
  }
  return true;
}

}  // namespace gnnLearningModule