#include "sc-agents-common/keynodes/coreKeynodes.hpp"
#include "sc-agents-common/utils/AgentUtils.hpp"
#include "sc-agents-common/utils/CommonUtils.hpp"
#include "sc-agents-common/utils/GenerationUtils.hpp"
#include "sc-agents-common/utils/IteratorUtils.hpp"

#include "keynodes/GNNLearningKeynodes.hpp"
#include "manager/GNNLearningManager.hpp"
#include "utils/ActionUtils.hpp"

#include "GNNLearningAgent.hpp"

using namespace gnnLearningModule;
using namespace scAgentsCommon;

SC_AGENT_IMPLEMENTATION(GNNLearningAgent)
{
  ScAddr actionAddr = otherAddr;
  if (!checkActionClass(actionAddr))
  {
    return SC_RESULT_OK;
  }

  SC_LOG_DEBUG("GNNLearningAgent started");

  auto manager = new GNNLearningManager(&m_memoryCtx);
  manager->manage({
      gnnLearningModule::GNNLearningKeynodes::sc_node_not_relation
  });

  SC_LOG_DEBUG("GNNLearningAgent finished");
  utils::AgentUtils::finishAgentWork(&m_memoryCtx, actionAddr, true);
  return SC_RESULT_OK;
}

bool GNNLearningAgent::checkActionClass(ScAddr const & actionAddr)
{
  return m_memoryCtx.HelperCheckEdge(
      GNNLearningKeynodes::action_train_gnn, actionAddr, ScType::EdgeAccessConstPosPerm);
}