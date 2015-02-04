# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 GNS3 Technologies Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from ..web.route import Route
from ..schemas.vpcs import VPCS_CREATE_SCHEMA
from ..schemas.vpcs import VPCS_UPDATE_SCHEMA
from ..schemas.vpcs import VPCS_OBJECT_SCHEMA
from ..schemas.vpcs import VPCS_NIO_SCHEMA
from ..modules.vpcs import VPCS


class VPCSHandler:

    """
    API entry points for VPCS.
    """

    @classmethod
    @Route.post(
        r"/vpcs",
        status_codes={
            201: "Instance created",
            400: "Invalid project UUID",
            409: "Conflict"
        },
        description="Create a new VPCS instance",
        input=VPCS_CREATE_SCHEMA,
        output=VPCS_OBJECT_SCHEMA)
    def create(request, response):

        vpcs = VPCS.instance()
        vm = yield from vpcs.create_vm(request.json["name"],
                                       request.json["project_id"],
                                       request.json.get("uuid"),
                                       console=request.json.get("console"),
                                       startup_script=request.json.get("startup_script"))
        response.set_status(201)
        response.json(vm)

    @classmethod
    @Route.get(
        r"/vpcs/{uuid}",
        parameters={
            "uuid": "Instance UUID"
        },
        status_codes={
            200: "Success",
            404: "Instance doesn't exist"
        },
        description="Get a VPCS instance",
        output=VPCS_OBJECT_SCHEMA)
    def show(request, response):

        vpcs_manager = VPCS.instance()
        vm = vpcs_manager.get_vm(request.match_info["uuid"])
        response.json(vm)

    @classmethod
    @Route.put(
        r"/vpcs/{uuid}",
        parameters={
            "uuid": "Instance UUID"
        },
        status_codes={
            200: "Instance updated",
            404: "Instance doesn't exist",
            409: "Conflict"
        },
        description="Update a VPCS instance",
        input=VPCS_UPDATE_SCHEMA,
        output=VPCS_OBJECT_SCHEMA)
    def update(request, response):

        vpcs_manager = VPCS.instance()
        vm = vpcs_manager.get_vm(request.match_info["uuid"])
        vm.name = request.json.get("name", vm.name)
        vm.console = request.json.get("console", vm.console)
        vm.startup_script = request.json.get("startup_script", vm.startup_script)
        response.json(vm)

    @classmethod
    @Route.delete(
        r"/vpcs/{uuid}",
        parameters={
            "uuid": "Instance UUID"
        },
        status_codes={
            204: "Instance deleted",
            404: "Instance doesn't exist"
        },
        description="Delete a VPCS instance")
    def delete(request, response):

        yield from VPCS.instance().delete_vm(request.match_info["uuid"])
        response.set_status(204)

    @classmethod
    @Route.post(
        r"/vpcs/{uuid}/start",
        parameters={
            "uuid": "Instance UUID"
        },
        status_codes={
            204: "Instance started",
            400: "Invalid VPCS instance UUID",
            404: "Instance doesn't exist"
        },
        description="Start a VPCS instance")
    def start(request, response):

        vpcs_manager = VPCS.instance()
        vm = vpcs_manager.get_vm(request.match_info["uuid"])
        yield from vm.start()
        response.set_status(204)

    @classmethod
    @Route.post(
        r"/vpcs/{uuid}/stop",
        parameters={
            "uuid": "Instance UUID"
        },
        status_codes={
            204: "Instance stopped",
            400: "Invalid VPCS instance UUID",
            404: "Instance doesn't exist"
        },
        description="Stop a VPCS instance")
    def stop(request, response):

        vpcs_manager = VPCS.instance()
        vm = vpcs_manager.get_vm(request.match_info["uuid"])
        yield from vm.stop()
        response.set_status(204)

    @classmethod
    @Route.post(
        r"/vpcs/{uuid}/reload",
        parameters={
            "uuid": "Instance UUID",
        },
        status_codes={
            204: "Instance reloaded",
            400: "Invalid instance UUID",
            404: "Instance doesn't exist"
        },
        description="Reload a VPCS instance")
    def reload(request, response):

        vpcs_manager = VPCS.instance()
        vm = vpcs_manager.get_vm(request.match_info["uuid"])
        yield from vm.reload()
        response.set_status(204)

    @Route.post(
        r"/vpcs/{uuid}/ports/{port_number:\d+}/nio",
        parameters={
            "uuid": "Instance UUID",
            "port_number": "Port where the nio should be added"
        },
        status_codes={
            201: "NIO created",
            400: "Invalid instance UUID",
            404: "Instance doesn't exist"
        },
        description="Add a NIO to a VPCS instance",
        input=VPCS_NIO_SCHEMA,
        output=VPCS_NIO_SCHEMA)
    def create_nio(request, response):

        vpcs_manager = VPCS.instance()
        vm = vpcs_manager.get_vm(request.match_info["uuid"])
        nio = vpcs_manager.create_nio(vm.vpcs_path, request.json)
        vm.port_add_nio_binding(int(request.match_info["port_number"]), nio)
        response.set_status(201)
        response.json(nio)

    @classmethod
    @Route.delete(
        r"/vpcs/{uuid}/ports/{port_number:\d+}/nio",
        parameters={
            "uuid": "Instance UUID",
            "port_number": "Port from where the nio should be removed"
        },
        status_codes={
            204: "NIO deleted",
            400: "Invalid instance UUID",
            404: "Instance doesn't exist"
        },
        description="Remove a NIO from a VPCS instance")
    def delete_nio(request, response):

        vpcs_manager = VPCS.instance()
        vm = vpcs_manager.get_vm(request.match_info["uuid"])
        vm.port_remove_nio_binding(int(request.match_info["port_number"]))
        response.set_status(204)
