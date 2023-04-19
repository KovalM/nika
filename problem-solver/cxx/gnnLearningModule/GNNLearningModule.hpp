#pragma once

#include "sc-memory/sc_memory.hpp"
#include "sc-memory/sc_module.hpp"

#include "agent/GNNLearningAgent.hpp"
#include "keynodes/GNNLearningKeynodes.hpp"
#include "utils/ActionUtils.hpp"

#include "GNNLearningModule.generated.hpp"

namespace gnnLearningModule
{
class GNNLearningModule : public ScModule
{
  SC_CLASS(LoadOrder(100))
  SC_GENERATED_BODY()

  virtual sc_result

  InitializeImpl() override;

  virtual sc_result ShutdownImpl() override;
};

}  // namespace gnnLearningModule
