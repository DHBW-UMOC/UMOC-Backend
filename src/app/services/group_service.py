import uuid
from datetime import datetime
from app.extensions import db
from app.models.group import Group, GroupMember, GroupRoleEnum


class GroupService:
    def create_group(self, user_id, group_name, group_pic, group_members):
        # Check if group name already exists
        existing_group = Group.query.filter_by(group_name=group_name).first()
        if existing_group:
            return {"error": "Group name already exists"}
        # Create new group
        new_group = Group(
            group_id=str(uuid.uuid4()),
            group_name=group_name,
            admin_user_id=user_id,
            group_picture=group_pic,
            created_at=datetime.utcnow()
        )
        db.session.add(new_group)

        # Add group members
        for member_id in group_members:
            new_member = GroupMember(
                group_id=new_group.group_id,
                user_id=member_id,
                role=GroupRoleEnum.MEMBER,
            )
            db.session.add(new_member)

        new_member = GroupMember(
            group_id=new_group.group_id,
            user_id=user_id,
            role=GroupRoleEnum.ADMIN,
        )
        db.session.add(new_member)
        try:
            db.session.commit()
            return {"success": True, "group_id": new_group.group_id}
        except Exception as e:
            db.session.rollback()
            return {"error": f"Database error: {str(e)}"}

    def delete_group(self, user_id, group_id):
        group = Group.query.filter_by(group_id=group_id).first()

        if not self.is_user_admin(user_id, group_id): return {"error": "User is not admin of the group"}
        if not group: return {"error": "Group not found"}

        GroupMember.query.filter_by(group_id=group_id).delete()

        db.session.delete(group)
        try:
            db.session.commit()
            return {"success": True}
        except Exception as e:
            db.session.rollback()
            return {"error": f"Database error: {str(e)}"}

    def add_member(self, user_id, group_id, new_member_id):
        if not self.does_group_exist(group_id): return {"error": "Group not found"}
        if not self.is_user_admin(user_id, group_id): return {"error": "User is not admin of the group"}

        new_member = GroupMember(
            group_id=group_id,
            user_id=new_member_id,
            role=GroupRoleEnum.MEMBER,
        )
        db.session.add(new_member)
        try:
            db.session.commit()
            return {"success": True}
        except Exception as e:
            db.session.rollback()
            return {"error": f"Database error: {str(e)}"}

    def remove_member(self, user_id, group_id, member_id):
        if not self.does_group_exist(group_id): return {"error": "Group not found"}
        if not self.is_user_admin(user_id, group_id): return {"error": "User is not admin of the group"}

        member = GroupMember.query.filter_by(group_id=group_id, user_id=member_id).first()
        if not member: return {"error": "Member not found"}

        db.session.delete(member)
        try:
            db.session.commit()
            return {"success": True}
        except Exception as e:
            db.session.rollback()
            return {"error": f"Database error: {str(e)}"}

    def change_group_name(self, user_id, group_id, new_name):
        if not self.does_group_exist(group_id): return {"error": "Group not found"}
        if not self.is_user_admin(user_id, group_id): return {"error": "User is not admin of the group"}

        group = Group.query.filter_by(group_id=group_id).first()
        if not group: return {"error": "Group not found"}

        group.group_name = new_name
        try:
            db.session.commit()
            return {"success": True}
        except Exception as e:
            db.session.rollback()
            return {"error": f"Database error: {str(e)}"}

    def change_group_picture(self, user_id, group_id, new_picture):
        if not self.does_group_exist(group_id): return {"error": "Group not found"}
        if not self.is_user_admin(user_id, group_id): return {"error": "User is not admin of the group"}

        group = Group.query.filter_by(group_id=group_id).first()
        if not group: return {"error": "Group not found"}

        group.group_picture = new_picture
        try:
            db.session.commit()
            return {"success": True}
        except Exception as e:
            db.session.rollback()
            return {"error": f"Database error: {str(e)}"}

    def change_group_admin(self, user_id, group_id, new_admin_id):
        if not self.does_group_exist(group_id): return {"error": "Group not found"}
        if not self.is_user_admin(user_id, group_id): return {"error": "User is not admin of the group"}

        group = Group.query.filter_by(group_id=group_id).first()
        if not group: return {"error": "Group not found"}

        member = GroupMember.query.filter_by(group_id=group_id, user_id=new_admin_id).first()
        if not member: return {"error": "Member not found"}

        member.role = GroupRoleEnum.ADMIN
        try:
            db.session.commit()
            return {"success": True}
        except Exception as e:
            db.session.rollback()
            return {"error": f"Database error: {str(e)}"}

    def leave_group(self, user_id, group_id):
        if not self.does_group_exist(group_id): return {"error": "Group not found"}
        if not self.is_user_member(user_id, group_id): return {"error": "User is not a member of the group"}

        member = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first()
        if not member: return {"error": "Member not found"}

        db.session.delete(member)
        try:
            db.session.commit()
            return {"success": True}
        except Exception as e:
            db.session.rollback()
            return {"error": f"Database error: {str(e)}"}

    ##############################
    ## HELPER FUNCTIONS
    ##############################

    def is_user_admin(self, user_id, group_id):
        group_member = GroupMember.query.filter_by(user_id=user_id, group_id=group_id).first()
        if group_member and group_member.role == GroupRoleEnum.ADMIN:
            return True
        return False

    def is_user_member(self, user_id, group_id):
        group_member = GroupMember.query.filter_by(user_id=user_id, group_id=group_id).first()
        if group_member:
            return True
        return False

    def does_group_exist(self, group_id):
        group = Group.query.filter_by(group_id=group_id).first()
        return group is not None

    def get_group_members(self, user_id, group_id):
        if not self.does_group_exist(group_id): return {"error": "Group not found"}
        if not self.is_user_admin(user_id, group_id): return {"error": "User is not admin of the group"}

        members = GroupMember.query.filter_by(group_id=group_id).all()
        result = []
        for member in members:
            user = member.user
            result.append({
                "contact_id": member.user_id,
                "name": user.username,
                "picture_url": user.profile_picture,
                "role": member.role.value
            })

        return result

    def get_group_by_id(self, group_id):
        group = Group.query.filter_by(group_id=group_id).first()
        if not group: return {"error": "Group not found"}

        return group.to_dict()

    def get_groups_by_user_id(self, user_id):
        group_ids = GroupMember.query.filter_by(user_id=user_id).all()
        #if not group_ids: return {"error": "No groups found for this user"}
        group_ids = [group.group_id for group in group_ids]
        groups = Group.query.filter(Group.group_id.in_(group_ids)).all()

        #if not groups: return {"error": "No groups found for this user"}

        return [{
            **group.to_dict(),
            "members": self.get_group_members(user_id, group.group_id)
        } for group in groups]

    def is_id_group(self, group_id):
        group = Group.query.filter_by(group_id=group_id).first()
        if not group: return False

        return True
