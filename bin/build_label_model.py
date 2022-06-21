"""
Script to build and save the labeling model.
"""
import logging

import argparse
import uuid
import copy
from emission.analysis.modelling.user_label_model.model_storage import ModelStorage
from emission.analysis.modelling.user_label_model.model_type import ModelType

import emission.pipeline.reset as epr
import emission.core.get_database as edb
import emission.core.wrapper.user as ecwu
import emission.storage.timeseries.abstract_timeseries as esta
import emission.analysis.modelling.user_label_model.run_model as eamur

def _get_user_list(args):
    if args.all:
        return _find_all_users()
    elif args.platform:
        return _find_platform_users(args.platform)
    elif args.email_list:
        return _email_2_user_list(args.email_list)
    else:
        assert args.user_list is not None
        return [uuid.UUID(u) for u in args.user_list]

def _find_platform_users(platform):
    # Since all new clients register a profile with the server, we don't have
    # to run a 'distinct' query over the entire contents of the timeseries.
    # Instead, we can simply query from the profile users, which is
    # significantly faster
    # Use the commented out line instead for better performance.
    # Soon, we can move to the more performant option, because there will be
    # no users that don't have a profile
    # return edb.get_timeseries_db().find({'metadata.platform': platform}).distinct(
    #    'user_id')
   return edb.get_profile_db().find({"curr_platform": platform}).distinct("user_id")

def _find_all_users():
   return esta.TimeSeries.get_uuid_list()

def _email_2_user_list(email_list):
    return [ecwu.User.fromEmail(e).uuid for e in email_list]

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s',
        level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-a", "--all", action="store_true", default=False,
        help="build the model for all users")
    group.add_argument("-p", "--platform", choices = ['android', 'ios'],
                        help="build the model for all on the specified platform")
    group.add_argument("-u", "--user_list", nargs='+',
        help="user ids to build the model for")
    group.add_argument("-e", "--email_list", nargs='+',
        help="email addresses to build the model for")

    args = parser.parse_args()
    print(args)

    user_list = _get_user_list(args)
    logging.info("received list with %s users" % user_list)
    for user_id in user_list:
        logging.info("building model for user %s" % user_id)
        model_type = ModelType.GREEDY_SIMILARITY_BINNING
        model_storage = ModelStorage.DATABASE
        min_trips = 14
        eamur.update_user_label_model(user_id, model_type, model_storage, min_trips)
