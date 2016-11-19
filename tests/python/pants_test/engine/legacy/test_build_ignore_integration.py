# coding=utf-8
# Copyright 2014 Pants project contributors (see CONTRIBUTORS.md).
# Licensed under the Apache License, Version 2.0 (see LICENSE).

from __future__ import (absolute_import, division, generators, nested_scopes, print_function,
                        unicode_literals, with_statement)

import os
import tempfile

from pants_test.pants_run_integration_test import PantsRunIntegrationTest, ensure_engine


class IgnorePatternsPantsIniIntegrationTest(PantsRunIntegrationTest):
  """Tests the functionality of the build_ignore_patterns option in pants.ini ."""

  @ensure_engine
  def test_build_ignore_patterns_pants_ini(self):
    def output_to_list(output_filename):
      with open(output_filename, 'r') as results_file:
        return set([line.rstrip() for line in results_file.readlines()])

    tempdir = tempfile.mkdtemp()
    tmp_output = os.path.join(tempdir, 'minimize-output1.txt')
    run_result = self.run_pants(['minimize',
                                 'testprojects::',
                                 '--quiet',
                                 '--minimize-output-file={0}'.format(tmp_output)])
    self.assert_success(run_result)
    results = output_to_list(tmp_output)
    self.assertIn('testprojects/src/java/org/pantsbuild/testproject/phrases:ten-thousand',
                  results)
    self.assertIn('testprojects/src/java/org/pantsbuild/testproject/phrases:once-upon-a-time',
                  results)
    self.assertIn('testprojects/src/java/org/pantsbuild/testproject/phrases:lesser-of-two',
                  results)
    self.assertIn('testprojects/src/java/org/pantsbuild/testproject/phrases:there-was-a-duck',
                  results)

    tmp_output = os.path.join(tempdir, 'minimize-output2.txt')

    run_result = self.run_pants(['minimize',
                                 'testprojects::',
                                 '--quiet',
                                 '--minimize-output-file={0}'.format(tmp_output)],
                                config={
                                    'DEFAULT': {
                                        'build_ignore': [
                                            'testprojects/src/java/org/pantsbuild/testproject/phrases'
                                        ]
                                    }
                                })
    self.assert_success(run_result)
    results = output_to_list(tmp_output)
    self.assertNotIn('testprojects/src/java/org/pantsbuild/testproject/phrases:ten-thousand',
                     results)
    self.assertNotIn('testprojects/src/java/org/pantsbuild/testproject/phrases:once-upon-a-time',
                     results)
    self.assertNotIn('testprojects/src/java/org/pantsbuild/testproject/phrases:lesser-of-two',
                     results)
    self.assertNotIn('testprojects/src/java/org/pantsbuild/testproject/phrases:there-was-a-duck',
                     results)

  @ensure_engine
  def test_build_ignore_dependency(self):
    run_result = self.run_pants(['-q',
                                 'list',
                                 'testprojects/tests/python/pants::'],
                                config={
                                  'DEFAULT': {
                                    'build_ignore': [
                                      'testprojects/src/'
                                    ]
                                  }
                                })

    self.assert_failure(run_result)
    # Error message complains dependency dir has no BUILD files.
    self.assertIn('testprojects/src/thrift/org/pantsbuild/constants_only', run_result.stderr_data)

  @ensure_engine
  def test_build_ignore_dependency_success(self):
    run_result = self.run_pants(['-q',
                                 'list',
                                 'testprojects/tests/python/pants::'],
                                config={
                                  'DEFAULT': {
                                    'build_ignore': [
                                      'testprojects/src/antlr'
                                    ]
                                  }
                                })

    self.assert_success(run_result)
    self.assertIn('testprojects/tests/python/pants/constants_only:constants_only', run_result.stdout_data)
