''' Sender '''
# pylint: disable=too-few-public-methods
from typing import Any, Generator, Literal, Optional, Union

from jinja2.sandbox import SandboxedEnvironment
from pymongo.collection import ReturnDocument
from pymongo.cursor import Cursor

import setting
from models.senderdb import (SenderCampaignDB, SenderLogsDB, SenderReceiverDB,
                             SenderSESLogsDB)
from module.awsses import AWSSES
from module.team import Team
from module.users import User


class SenderCampaign:
    ''' SenderCampaign class '''

    @staticmethod
    def create(name: str, pid: str, tid: str, uid: str) -> dict[str, Any]:
        ''' Create new campaign

        Args:
            name (str): Campaign name.
            pid (str): Project id.
            tid (str): Team id.
            uid (str): User id.

        Returns:
            Return the added data.

        '''

        data = SenderCampaignDB.new(
            name=name.strip(), pid=pid, tid=tid, uid=uid)
        return SenderCampaignDB().add(data)

    @staticmethod
    def get(cid: str, pid: Optional[str] = None,
            tid: Optional[str] = None) -> Optional[dict[str, Any]]:
        ''' Get campaign

        Args:
            cid (str): Campaign id.
            pid (str): Project id.
            tid (str): Team id.

        Returns:
            Return the campaign data.

        '''
        query = {'_id': cid}

        if pid is not None:
            query['created.pid'] = pid

        if tid is not None:
            query['created.tid'] = tid

        return SenderCampaignDB().find_one(query)

    @staticmethod
    def get_list(pid: str, tid: str) -> Cursor[dict[str, Any]]:
        ''' Get list campaign

        Args:
            pid (str): Project id.
            tid (str): Team id.

        Returns:
            Return the [pymongo.cursor.Cursor][].

        '''
        return SenderCampaignDB().find({'created.pid': pid, 'created.tid': tid})

    @staticmethod
    def save_mail(cid: str, subject: str, content: str,
                  preheader: str, layout: Literal['1', '2']) -> dict[str, Any]:
        ''' Save mail data

        Args:
            cid (str): Campaign id.
            subject (str): Mail subject.
            content (str): Mail content.
            preheader (str): The preheader in mail.
            layout (str): In which layout. `1`: In Volunteer layout. `2`: In COSCUP layout.

        Returns:
            Return the added / updated data.

        '''
        return SenderCampaignDB().find_one_and_update(
            {'_id': cid},
            {'$set': {
                'mail.subject': subject,
                'mail.content': content,
                'mail.preheader': preheader,
                'mail.layout': layout,
            }},
            return_document=ReturnDocument.AFTER,
        )

    @staticmethod
    def save_receiver(cid: str, teams: list[str], team_w_tags: dict[str, list[str]],
                      users: Optional[dict[str, Any]] = None,
                      all_users: bool = False) -> dict[str, Any]:
        ''' Save receiver

        Args:
            cid (str): Campaign id.
            teams (list): List of `tid`.
            team_w_tags (dict): With team's internal tags. `{'<tid>': [<tag>, ...]}`.
            users (list): List of user/mail. `{'name': <username>, 'mail': <mail>}`.
                          **(not in completed implement)**
            all_users (bool): All volunteers in platform.

        '''
        update: dict[str, Any] = {'receiver.teams': teams}
        update['receiver.users'] = users if users else []
        update['receiver.all_users'] = all_users
        update['receiver.team_w_tags'] = team_w_tags

        return SenderCampaignDB().find_one_and_update(
            {'_id': cid},
            {'$set': update},
            return_document=ReturnDocument.AFTER,
        )


class SenderMailer:
    ''' Sender Mailer

    Args:
        template_path (str): Mail template path.
        subject (str): Mail subject.
        source (dict): Mail `FROM`, `{'name': <name>, 'mail': <mail>}`.

    '''

    def __init__(self, template_path: str, subject: str,
                 content: dict[str, Any], source: Optional[dict[str, str]] = None) -> None:
        with open(template_path, 'r', encoding='UTF8') as files:
            body = SandboxedEnvironment().from_string(files.read()).render(**content)

            self.tpl = SandboxedEnvironment().from_string(body)
            self.subject = SandboxedEnvironment().from_string(subject)

            if source is None:
                source = setting.AWS_SES_FROM

            if 'text_body' in content and content['text_body']:
                self.text_body = SandboxedEnvironment(
                ).from_string(content['text_body'])

            self.awsses = AWSSES(aws_access_key_id=setting.AWS_ID,
                                 aws_secret_access_key=setting.AWS_KEY, source=source)

    def send(self, to_list: list[dict[str, str]],
             data: dict[str, Any], x_coscup: Optional[str] = None) -> Any:
        ''' Send mail

        Args:
            to_list (list): List of user/mail in `{'name': <name>, 'mail': <mail>}`.
            data (dict): Mail datas. More details: [module.awsses.AWSSES.raw_mail][].

        Returns:
            More details: [module.awsses.AWSSES.send_raw_email][].

        '''
        raw_mail = self.awsses.raw_mail(
            to_addresses=to_list,
            subject=self.subject.render(**data),
            body=self.tpl.render(**data),
            text_body=self.text_body.render(**data),
            x_coscup=x_coscup,
            list_unsubscribe=setting.AWS_LIST_UNSUBSCRIBE,
        )
        return self.awsses.send_raw_email(data=raw_mail)


class SenderMailerVolunteer(SenderMailer):
    ''' Sender using volunteer template

    Args:
        subject (str): Mail subject.
        source (dict): Mail `FROM`, `{'name': <name>, 'mail': <mail>}`.

    '''

    def __init__(self, subject: str, content: dict[str, Any],
                 source: Optional[dict[str, str]] = None) -> None:
        super().__init__(
            template_path='/app/templates/mail/sender_base.html',
            subject=subject, content=content, source=source)


class SenderMailerCOSCUP(SenderMailer):
    ''' Sender using COSCUP template

    Args:
        subject (str): Mail subject.
        source (dict): Mail `FROM`, `{'name': <name>, 'mail': <mail>}`.

    '''

    def __init__(self, subject: str, content: dict[str, Any],
                 source: Optional[dict[str, str]] = None):
        super().__init__(
            template_path='/app/templates/mail/coscup_base.html',
            subject=subject, content=content, source=source)


class SenderLogs:
    ''' SenderLogs object '''

    @staticmethod
    def save(cid: str, layout: str, desc: str, receivers: list[dict[str, Any]]) -> None:
        ''' save log

        :param str cid: cid
        :param str layout: layout
        :param str desc: desc
        :param list receivers: receivers

        '''
        SenderLogsDB().add(cid=cid, layout=layout, desc=desc, receivers=receivers)

    @staticmethod
    def get(cid: str) -> Generator[dict[str, Any], None, None]:
        ''' Get log

        :param str cid: cid

        '''
        for raw in SenderLogsDB().find({'cid': cid}, sort=(('_id', -1), )):
            yield raw


class SenderSESLogs:
    ''' SenderSESLogs '''

    @staticmethod
    def save(cid: str, name: str, mail: str, result: dict[str, Any]) -> None:
        ''' Save log

        Args:
            cid (str): Campaign id.
            name (str): User name.
            mail (str): User mail.
            result (str): The result from [SES.Client.send_email][], [SES.Client.send_raw_email][].

        '''
        SenderSESLogsDB().add(cid=cid, mail=mail, name=name, ses_result=result)


class SenderReceiver:
    ''' SenderReceiver object '''

    @staticmethod
    def replace(pid: str, cid: str, datas: list[dict[str, Any]]) -> int:
        ''' Replace

        Args:
            pid (str): Project id.
            cid (str): Campaign id.
            datas (list): List of receiver datas. `name`, `mail` are required
                or include `uid` for auto replace the `name`, `mail` value.

        '''
        sender_receiver_db = SenderReceiverDB()
        sender_receiver_db.remove_past(pid=pid, cid=cid)

        uids = []
        for data in datas:
            if 'uid' in data and data['uid']:
                uids.append(data['uid'])

        user_infos = User.get_info(uids=uids)
        user_info_uids = {}
        for uid, data in user_infos.items():
            user_info_uids[uid] = {
                'name': data['profile']['badge_name'],
                'mail': data['oauth']['email'],
            }

        save_datas = []
        for data in datas:
            if 'uid' in data and data['uid'] and data['uid'] in user_info_uids:
                _data = SenderReceiverDB.new(pid=pid, cid=cid,
                                             name=user_info_uids[data['uid']
                                                                 ]['name'],
                                             mail=user_info_uids[data['uid']
                                                                 ]['mail'],
                                             )
            else:
                _data = SenderReceiverDB.new(
                    pid=pid, cid=cid, name=data['name'], mail=data['mail'])

            _data['data'].update(data)
            save_datas.append(_data)

        sender_receiver_db.update_data(pid=pid, cid=cid, datas=save_datas)

        return len(save_datas)

    @staticmethod
    def update(pid: str, cid: str, datas: list[dict[str, Any]]) -> int:
        ''' Update

        Args:
            pid (str): Project id.
            cid (str): Campaign id.
            datas (list): List of receiver datas. `name`, `mail` are required
                or include `uid` for auto replace the `name`, `mail` value.

        '''
        uids = []
        for data in datas:
            if 'uid' in data and data['uid']:
                uids.append(data['uid'])

        user_infos = User.get_info(uids=uids)
        user_info_uids = {}
        for uid, data in user_infos.items():
            user_info_uids[uid] = {
                'name': data['profile']['badge_name'],
                'mail': data['oauth']['email'],
            }

        save_datas = []
        for data in datas:
            if 'uid' in data and data['uid'] and data['uid'] in user_info_uids:
                _data = SenderReceiverDB.new(pid=pid, cid=cid,
                                             name=user_info_uids[data['uid']
                                                                 ]['name'],
                                             mail=user_info_uids[data['uid']
                                                                 ]['mail'],
                                             )
            else:
                _data = SenderReceiverDB.new(
                    pid=pid, cid=cid, name=data['name'], mail=data['mail'])

            _data['data'].update(data)
            save_datas.append(_data)

        SenderReceiverDB().update_data(pid=pid, cid=cid, datas=save_datas)

        return len(save_datas)

    @staticmethod
    def remove(pid: str, cid: str) -> int:
        ''' Update

        Args:
            pid (str): Project id.
            cid (str): Campaign id.

        '''
        return SenderReceiverDB().remove_past(pid=pid, cid=cid)

    @staticmethod
    def get(pid: str, cid: str) -> tuple[list[str], list[list[str]]]:
        ''' Get

        Args:
            pid (str): Project id.
            cid (str): Campaign id.

        Returns:
            Return a tuple with all fields at first. The second is the all datas.

        '''
        datas = list(SenderReceiverDB().find({'pid': pid, 'cid': cid}))
        fields = ['name', 'mail']
        for data in datas:
            for k in data['data']:
                if k not in ('name', 'mail') and k not in fields:
                    fields.append(k)

        raws = []
        for data in datas:
            raw = []
            for field in fields:
                raw.append(data['data'].get(field, ''))

            raws.append(raw)

        return fields, raws

    @staticmethod
    def get_from_user(pid: str,
                      tids: Union[str, list[str]]) -> tuple[tuple[str, str], list[list[str]]]:
        ''' Get users from userdb by project, team

        Args:
            pid (str): Project id.
            tids (list): List of `tid`.

        Returns:
            Return a tuple with `('name', 'mail')` at first. The second is the all datas.

        '''
        _tids: list[str]

        if isinstance(tids, str):
            _tids = [tids, ]
        else:
            _tids = tids

        team_users = Team.get_users(pid=pid, tids=_tids)
        uids = []
        for user_ids in team_users.values():
            uids.extend(user_ids)

        user_infos = User.get_info(uids=uids)
        datas = []
        for value in user_infos.values():
            # append, plus more data here in the future
            datas.append({
                'name': value['profile']['badge_name'],
                'mail': value['oauth']['email'],
            })

        raws = []
        for data in datas:
            raw = []
            for field in ('name', 'mail'):
                raw.append(data[field])

            raws.append(raw)

        return (('name', 'mail'), raws)

    @staticmethod
    def get_all_users() -> tuple[tuple[str, str], list[tuple[str, str]]]:
        ''' Get all users

        Returns:
            Return a tuple with `('name', 'mail')` at first. The second is the all datas.

        '''
        uids = []
        for user in User.get_all_users():
            uids.append(user['_id'])

        user_infos = User.get_info(uids=uids)
        raws = []
        for value in user_infos.values():
            raws.append((
                value['profile']['badge_name'],
                value['oauth']['email'],
            ))

        return (('name', 'mail'), raws)

    @staticmethod
    def get_by_tags(pid: str, tid: str,
                    tags: list[str]) -> tuple[tuple[str, str], list[tuple[str, str]]]:
        ''' Get users by tags

        Returns:
            Return a tuple with `('name', 'mail')` at first. The second is the all datas.

        '''
        uids = Team.get_members_uid_by_tags(pid=pid, tid=tid, tags=tags)

        user_infos = User.get_info(uids=uids)
        raws = []
        for value in user_infos.values():
            raws.append((
                value['profile']['badge_name'],
                value['oauth']['email'],
            ))

        return (('name', 'mail'), raws)
