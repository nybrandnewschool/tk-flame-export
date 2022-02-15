# Copyright (c) 2014 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

from __future__ import absolute_import
import os
import re

import sgtk
from sgtk.platform.qt import QtCore, QtGui


class ContextSelector(sgtk.get_hook_baseclass()):
    """
    This hook is used to determine the Entity which the Exported media and cut info
    should be uploaded to. Shots will be created within the Entity returned by find_entity
    or new_entity.
    """

    def find_entity(self, info):
        """Called during the preExportSequence Flame hook by app.pre_export_sequence.

        Should Return a ShotGrid Entity that the Flame Sequence represents.

        Arguments:
            info (dict): Info from preExportSequence Flame hook.

        Returns:
            dict - ShotGrid Entity with ['type', 'id', 'code'] keys.
            None - No matching Entity found. This will result in the new_entity
                   method running.
        """

        shotgun = self.parent.shotgun
        context = self.parent.context

        # Name lookups
        potential_names = [info['sequenceName']]

        # Name without "v000" version specifier on end
        match = re.search(r'[-_ ]v(\d+)', info['sequenceName'])
        if match:
            name = info['sequenceName'].split(match.group())[0]
            potential_names.append(name)

        entity = shotgun.find_one(
            self.parent.get_setting('shot_parent_entity_type'),
            [['code', 'in', potential_names], ['project', 'is', context.project]],
            ['code'],
        )
        if entity:
            return entity

    def new_entity(self, info):
        """Called during the preExportAsset Flame hook by app.populate_shotgun.

        When find_entity returns None, this method is called to create a new_entity
        based on the Flame Hook info.

        Arguments:
            info (dict): Info from preExportAsset Flame hook.

        Returns:
            dict - ShotGrid Entity with ['type', 'id', 'code'] keys.
            None/False - Cancel Upload.
        """

        entity_name = re.split(r'[-_ ]v\d+', info['sequenceName'])[0]
        message = (
            'No Entity matching <b>%s</b> was found.<br><br>'
            '<b>Select</b> an Entity or create a <b>New</b> one.<br>'
        ) % entity_name

        return self.parent.request_upload_context(
            message=message,
            defaults={
                'mode': 0,  # Open New tab
                'entity_name': entity_name,
                'entity_type': self.parent.get_setting('shot_parent_entity_type'),
                'task_template': self.parent.get_setting('shot_parent_task_template'),
                'shot_task_template': self.parent.get_setting('task_template'),
            },
        )