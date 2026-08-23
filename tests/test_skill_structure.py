"""Structure checks for the shipped skill: every file SKILL.md points to exists,
every command has a playbook, and playbooks don't point at missing files.

Run: python3 -m unittest discover -s tests -v
"""

import os
import re
import sys
import unittest

sys.dont_write_bytecode = True
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL = os.path.join(ROOT, "skills", "serpwise")
REF_RE = re.compile(r"`((?:references|commands|scripts)/[A-Za-z0-9_./-]+)`")


def read(rel):
    """Read a file inside the skill folder."""
    with open(os.path.join(SKILL, rel), encoding="utf-8") as fh:
        return fh.read()


class SkillStructureTests(unittest.TestCase):
    """The skill's internal links and command table stay consistent."""

    def test_skill_md_paths_exist(self):
        missing = [
            p for p in set(REF_RE.findall(read("SKILL.md"))) if not os.path.exists(os.path.join(SKILL, p))
        ]
        self.assertEqual(missing, [], "SKILL.md points at missing files")

    def test_every_command_has_playbook_and_vice_versa(self):
        table = re.findall(r"^\| `([a-z]+)[^`]*` \|.*`commands/", read("SKILL.md"), re.M)
        files = sorted(f[:-3] for f in os.listdir(os.path.join(SKILL, "commands")) if f.endswith(".md"))
        self.assertEqual(sorted(table), files)

    def test_playbook_paths_exist(self):
        for f in os.listdir(os.path.join(SKILL, "commands")):
            for p in set(REF_RE.findall(read("commands/" + f))):
                self.assertTrue(os.path.exists(os.path.join(SKILL, p)), f"{f}: {p}")

    def test_size_budget(self):
        body = read("SKILL.md")
        self.assertLess(body.count("\n"), 500)
        desc = re.search(r"^description: (.*)$", body, re.M).group(1)
        self.assertLessEqual(len(desc), 1024)

    def test_no_host_specific_paths(self):
        for rel in ["SKILL.md"] + ["commands/" + f for f in os.listdir(os.path.join(SKILL, "commands"))]:
            self.assertNotIn("~/.claude", read(rel), rel)


if __name__ == "__main__":
    unittest.main()
