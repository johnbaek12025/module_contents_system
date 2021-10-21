"""
- ctrl+c dose not work with DISABLE_OOB = ON in sqlnet.ora
- run the below code as a makeshift
  $ kill -9 `ps -ef | grep "python bin/ad-manager.py" | grep -v grep | awk '{print $2}'` 
"""

__appname__ = "analysis-contents-manager"
__version__ = "1.0"


import optparse
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

import adm
from adm.control_manager import ControlManager


if __name__ == "__main__":
    usage = """%prog [options]"""
    parser = optparse.OptionParser(usage=usage, description=__doc__)
    parser.add_option(
        "--deal-date", metavar="DEAL_DATE", dest="deal_date", help="test request"
    )
    parser.add_option(
        "--info-code", metavar="INFO_CODE", dest="info_code", help="test request"
    )
    parser.add_option(
        "--info-seq", metavar="INFO_SEQ", dest="info_seq", help="test request"
    )

    parser.add_option(
        "--request-type",
        metavar="REQUEST_TYPE",
        dest="request_type",
        help="test request",
    )

    parser.add_option(
        "--is-manual", metavar="IS_MANUAL", dest="is_manual", help="test request"
    )

    adm.add_basic_options(parser)
    (options, args) = parser.parse_args()

    config_dict = adm.read_config_file(options.config_file)

    config_dict["app_name"] = __appname__
    log_dict = config_dict.get("log", {})
    log_file_name = "adm.log"
    adm.setup_logging(
        appname=__appname__,
        appvers=__version__,
        filename=log_file_name,
        dirname=options.log_dir,
        debug=options.debug,
        log_dict=log_dict,
        emit_platform_info=True,
    )

    request = {}
    if options.deal_date:
        request["deal_date"] = options.deal_date
    if options.request_type:
        request["info_seq"] = options.info_seq
    if options.info_code:
        request["info_code"] = options.info_code
    if options.request_type:
        request["request_type"] = options.request_type
    if options.is_manual:
        request["is_manual"] = options.is_manual

    control_manager = ControlManager()
    control_manager.initialize(config_dict)

    if request != {}:
        control_manager.run(test_data=request)
    else:
        control_manager.run()
