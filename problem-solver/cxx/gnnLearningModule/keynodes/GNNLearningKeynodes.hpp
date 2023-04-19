#pragma once

#include "sc-memory/sc_addr.hpp"
#include "sc-memory/sc_object.hpp"

#include "GNNLearningKeynodes.generated.hpp"

namespace gnnLearningModule
{
class GNNLearningKeynodes : public ScObject
{
  SC_CLASS()
  SC_GENERATED_BODY()

public:
  SC_PROPERTY(Keynode("action_train_gnn"), ForceCreate)
  static ScAddr action_train_gnn;

  SC_PROPERTY(Keynode("sc_node_not_relation"), ForceCreate)
  static ScAddr sc_node_not_relation;

  SC_PROPERTY(Keynode("sc_node_norole_relation"), ForceCreate)
  static ScAddr sc_node_norole_relation;

  SC_PROPERTY(Keynode("sc_node_role_relation"), ForceCreate)
  static ScAddr sc_node_role_relation;
};

}  // namespace gnnLearningModule
