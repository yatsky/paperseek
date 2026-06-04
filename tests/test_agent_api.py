import unittest


class AgentApiTest(unittest.TestCase):
    def test_paperseek_agent_is_primary_public_name(self):
        from paperseek import LiteratureSearchAgent, PaperSeekAgent, WosSearchAgent
        from paperseek.search_agent import PaperSeekAgent as SearchModuleAgent
        from paperseek_core import PaperSeekAgent as CoreAgent

        self.assertIs(PaperSeekAgent, CoreAgent)
        self.assertIs(SearchModuleAgent, CoreAgent)
        self.assertIs(LiteratureSearchAgent, CoreAgent)
        self.assertIs(WosSearchAgent, CoreAgent)


if __name__ == "__main__":
    unittest.main()
