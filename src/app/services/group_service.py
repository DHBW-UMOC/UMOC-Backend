import uuid
from datetime import datetime
from app import db
from app.models.group import Group, GroupMember, GroupRoleEnum


class GroupService:
    def create_group(self, user_id, group_name, group_pic, group_members):
        
        # Create new group
        new_group = Group(
            group_id=str(uuid.uuid4()),
            group_name=group_name,
            admin_user_id=user_id,
            group_picture=group_pic,
            created_at=datetime.utcnow()
        )
        db.session.add(new_group)

        # Add the creator as a member
        new_member = GroupMember(
            group_id=new_group.group_id,
            user_id=user_id,
            role=GroupRoleEnum.ADMIN,
        )


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
            return {
                "group": new_group,
                "members": self.get_group_members(new_group.group_id),
                "am_admin": True  # Creator is always admin
            }
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

    def change_group_admin(self, user_id, group_id, target_user_id, method):
        if method not in ["add", "remove"]:
            return {"error": "Invalid method. Use 'add' or 'remove'."}
        
        if not self.does_group_exist(group_id): return {"error": "Group not found"}
        if not self.is_user_admin(user_id, group_id): return {"error": "User is not admin of the group"}

        group = Group.query.filter_by(group_id=group_id).first()
        if not group: return {"error": "Group not found"}

        member = GroupMember.query.filter_by(group_id=group_id, user_id=target_user_id).first()
        if not member: return {"error": "Member not found"}

        if method == "add":
            member.role = GroupRoleEnum.ADMIN
        elif method == "remove":
            # Count current admins
            admin_count = GroupMember.query.filter_by(group_id=group_id, role=GroupRoleEnum.ADMIN).count()
            if admin_count <= 1:
                return {"error": "Cannot remove the last admin from the group."}
            member.role = GroupRoleEnum.MEMBER
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

    def get_group_members(self, group_id):
        if not self.does_group_exist(group_id): return {"error": "Group not found"}

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
        group_ids = [group.group_id for group in group_ids]
        groups = Group.query.filter(Group.group_id.in_(group_ids)).all()

        return [{
            **group.to_dict(),
            "am_admin": self.is_user_admin(user_id, group.group_id),
            "members": self.get_group_members(group.group_id)
        } for group in groups]

    def is_id_group(self, group_id):
        group = Group.query.filter_by(group_id=group_id).first()
        if not group: return False

        return True
