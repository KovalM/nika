#include "GNNLearningModule.hpp"

#include "manager/GNNLearningManager.hpp"

using namespace gnnLearningModule;

SC_IMPLEMENT_MODULE(GNNLearningModule)

sc_result GNNLearningModule::InitializeImpl()
{
  if (!gnnLearningModule::GNNLearningKeynodes::InitGlobal())
  {
    return SC_RESULT_ERROR;
  }

  ScMemoryContext ctx(sc_access_lvl_make_min, "MessageReplyModule");
  if (ActionUtils::isActionDeactivated(&ctx, GNNLearningKeynodes::action_train_gnn))
  {
    SC_LOG_ERROR("action_train_gnn is deactivated");
  }
  else
  {
    SC_AGENT_REGISTER(GNNLearningAgent);
  }

  auto manager = new GNNLearningManager(&ctx);
  manager->manage({
      gnnLearningModule::GNNLearningKeynodes::sc_node_not_relation,
      gnnLearningModule::GNNLearningKeynodes::sc_node_role_relation,
      gnnLearningModule::GNNLearningKeynodes::sc_node_norole_relation,
  });

  return SC_RESULT_OK;
}

sc_result GNNLearningModule::ShutdownImpl()
{
  SC_AGENT_UNREGISTER(GNNLearningAgent);

  return SC_RESULT_OK;
}
