set(SOURCES
    "GNNLearningModule.cpp"
    "keynodes/GNNLearningKeynodes.cpp"
    "agent/GNNLearningAgent.cpp"
)

set(HEADERS
    "GNNLearningModule.hpp"
    "keynodes/GNNLearningKeynodes.hpp"
    "agent/GNNLearningAgent.hpp"
		manager/GNNLearningManager.cpp manager/GNNLearningManager.hpp model/Graph.hpp model/SampleElement.hpp translator/SampleToJsonFileTranslator.cpp translator/SampleToJsonFileTranslator.hpp)

include_directories(
    ${CMAKE_CURRENT_LIST_DIR}
    ${SC_MEMORY_SRC}
    ${SC_KPM_SRC}
    ${SC_TOOLS_SRC}
    ${SC_COMMON_MODULE_SRC}
)

add_library(gnnLearningModule SHARED ${SOURCES} ${HEADERS})
target_link_libraries(gnnLearningModule sc-memory sc-agents-common common nlohmann_json::nlohmann_json)

sc_codegen_ex(gnnLearningModule ${CMAKE_CURRENT_LIST_DIR} ${CMAKE_CURRENT_LIST_DIR}/generated)
