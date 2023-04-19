#pragma once

#include "model/SampleElement.hpp"

namespace gnnLearningModule
{
class SampleToJsonFileTranslator
{
private:
  std::string const JSON_TARGET_KEY = "target";
  std::string const JSON_LABELS_KEY = "labels";
  std::string const JSON_EDGES_KEY = "edges";

public:
  SampleToJsonFileTranslator() = default;

  bool translate(std::list<SampleElement *> const & sample, std::string const & path) const;
};
}