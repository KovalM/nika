#pragma once

#include "sc-memory/kpm/sc_agent.hpp"
#include "sc-agents-common/keynodes/coreKeynodes.hpp"

#include "GNNLearningAgent.generated.hpp"

namespace gnnLearningModule
{
class GNNLearningAgent : public ScAgent
{
  SC_CLASS(Agent, Event(scAgentsCommon::CoreKeynodes::question_initiated, ScEvent::Type::AddOutputEdge))
  SC_GENERATED_BODY()

private:
  int WAIT_TIME = 50000;

  bool checkActionClass(ScAddr const & actionAddr);
};

}  // namespace gnnLearningModule
