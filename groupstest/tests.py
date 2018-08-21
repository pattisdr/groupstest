from django.test import TestCase
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission, User
from groups_manager.models import Group, GroupType, Member, GroupMemberRole

from groupstest.models import Node


class GroupsTestCase(TestCase):

    def test_groups(self):
        # Node objects
        n1 = Node.objects.create(title='Node 1')  # n1
        n2 = Node.objects.create(title='Node 2', parent=n1)  # n1 -> n2
        n3 = Node.objects.create(title='Node 3', parent=n2)  # n1 -> n2 -> n3

        # Group Types (Optional)
        type_read = GroupType.objects.create(label='read')
        type_write = GroupType.objects.create(label='write')
        type_admin = GroupType.objects.create(label='admin')

        # Create Node Groups
        node_group_1_read = Group.objects.create(name=f'n:{n1.id}:read', group_type=type_read)
        node_group_1_write = Group.objects.create(name=f'n:{n1.id}:write', group_type=type_write)
        node_group_1_admin = Group.objects.create(name=f'n:{n1.id}:admin', group_type=type_admin)
        #
        node_group_2_read = Group.objects.create(name=f'n:{n2.id}:read', group_type=type_read)
        node_group_2_write = Group.objects.create(name=f'n:{n2.id}:write', group_type=type_write)
        node_group_2_admin = Group.objects.create(name=f'n:{n2.id}:admin', group_type=type_admin, parent=node_group_1_admin)
        #
        node_group_3_read = Group.objects.create(name=f'n:{n3.id}:read', group_type=type_read)
        node_group_3_write = Group.objects.create(name=f'n:{n3.id}:write', group_type=type_write)
        node_group_3_admin = Group.objects.create(name=f'n:{n3.id}:admin', group_type=type_admin, parent=node_group_2_admin)

        # Attach Node Groups to Node Objects (admins w/ implicit upstream view/read)
        #
        node_group_1_read.assign_object(n1, custom_permissions={'group': ['view']})
        node_group_1_write.assign_object(n1, custom_permissions={'group': ['view', 'change']})
        node_group_1_admin.assign_object(n1, custom_permissions={'group': ['view', 'change', 'delete'], 'groups_upstream': ['view']})
        #
        node_group_2_read.assign_object(n2, custom_permissions={'group': ['view']})
        node_group_2_write.assign_object(n2, custom_permissions={'group': ['view', 'change']})
        node_group_2_admin.assign_object(n2, custom_permissions={'group': ['view', 'change', 'delete'], 'groups_upstream': ['view']})
        #
        node_group_3_read.assign_object(n3, custom_permissions={'group': ['view']})
        node_group_3_write.assign_object(n3, custom_permissions={'group': ['view', 'change']})
        node_group_3_admin.assign_object(n3, custom_permissions={'group': ['view', 'change', 'delete'], 'groups_upstream': ['view']})

        # Members
        member_1 = Member.objects.create(first_name='Member', last_name='One')
        member_2 = Member.objects.create(first_name='Member', last_name='Two')
        member_3 = Member.objects.create(first_name='Member', last_name='Three')

        # Default Member Permissions
        node_group_1_read.add_member(member_1)
        node_group_1_write.add_member(member_1)
        node_group_1_admin.add_member(member_1)
        #
        node_group_2_read.add_member(member_2)
        node_group_2_write.add_member(member_2)
        node_group_2_admin.add_member(member_2)
        #
        node_group_3_read.add_member(member_3)
        node_group_3_write.add_member(member_3)
        node_group_3_admin.add_member(member_3)

        # Verify Explicit Admin Permission (no admin upstream permissions from nested group)
        self.assertFalse(member_3.has_perm('delete_node', n1))
        self.assertFalse(member_3.has_perm('delete_node', n2))
        self.assertTrue(member_3.has_perm('delete_node', n3))

        # Verify Implicit Read Permission from Admin
        self.assertTrue(member_1.has_perm('view_node', n2))
        self.assertFalse(member_1.has_perm('change_node', n2))
        self.assertFalse(member_1.has_perm('delete_node', n2))
        #
        self.assertTrue(member_1.has_perm('view_node', n3))
        self.assertFalse(member_1.has_perm('change_node', n3))
        self.assertFalse(member_1.has_perm('delete_node', n3))
        #
        self.assertTrue(member_2.has_perm('view_node', n3))
        self.assertFalse(member_2.has_perm('change_node', n3))
        self.assertFalse(member_2.has_perm('delete_node', n3))

        self.assertFalse(member_3.has_perm('view_node', n1))
        self.assertFalse(member_3.has_perm('change_node', n1))
        self.assertFalse(member_3.has_perm('delete_node', n1))

        # Other Members (Read)
        other_read = Member.objects.create(first_name='Other', last_name='Read')

        # Other Member Permissions
        node_group_1_read.add_member(other_read)

        # Verify Other Permission
        self.assertTrue(other_read.has_perm('view_node', n1))
        self.assertFalse(other_read.has_perm('change_node', n1))
        self.assertFalse(other_read.has_perm('delete_node', n1))
        #
        self.assertFalse(other_read.has_perm('view_node', n2))
        self.assertFalse(other_read.has_perm('change_node', n2))
        self.assertFalse(other_read.has_perm('delete_node', n2))
        #
        self.assertFalse(other_read.has_perm('view_node', n3))
        self.assertFalse(other_read.has_perm('change_node', n3))
        self.assertFalse(other_read.has_perm('delete_node', n3))

        # Other Members (Write)
        other_write = Member.objects.create(first_name='Other', last_name='Write')

        # Other Member Permissions
        node_group_1_write.add_member(other_write)

        # Verify Other Permission
        self.assertTrue(other_write.has_perm('view_node', n1))
        self.assertTrue(other_write.has_perm('change_node', n1))
        self.assertFalse(other_write.has_perm('delete_node', n1))
        #
        self.assertFalse(other_write.has_perm('view_node', n2))
        self.assertFalse(other_write.has_perm('change_node', n2))
        self.assertFalse(other_write.has_perm('delete_node', n2))
        #
        self.assertFalse(other_write.has_perm('view_node', n3))
        self.assertFalse(other_write.has_perm('change_node', n3))
        self.assertFalse(other_write.has_perm('delete_node', n3))

        # Other Members (Admin)
        other_admin = Member.objects.create(first_name='Other', last_name='Admin')

        # Other Member Permissions
        node_group_1_admin.add_member(other_admin)

        # Verify Other Permission
        self.assertTrue(other_admin.has_perm('view_node', n1))
        self.assertTrue(other_admin.has_perm('change_node', n1))
        self.assertTrue(other_admin.has_perm('delete_node', n1))
        #
        self.assertTrue(other_admin.has_perm('view_node', n2))
        self.assertFalse(other_admin.has_perm('change_node', n2))
        self.assertFalse(other_admin.has_perm('delete_node', n2))
        #
        self.assertTrue(other_admin.has_perm('view_node', n3))
        self.assertFalse(other_admin.has_perm('change_node', n3))
        self.assertFalse(other_admin.has_perm('delete_node', n3))

    def test_osf_groups(self):
        # Creating Platform team OSF Group
        osf_platform_managers = Group.objects.create(name='platform_manager')
        osf_platform_members = Group.objects.create(name='platform_member')

        content_type = ContentType.objects.get_for_model(Group)
        manage_permission = Permission.objects.create(
            codename='manage_group',
            name='Can manage group membership',
            content_type=content_type
        )

        # Add manage permissions to the manager group for both the manager and member groups
        osf_platform_managers.assign_object(osf_platform_managers, custom_permissions={'group': ['manage_group']})
        osf_platform_managers.assign_object(osf_platform_members, custom_permissions={'group': ['manage_group']})

        # Members
        casey = Member.objects.create(first_name='Casey')
        dawn = Member.objects.create(first_name='Dawn')
        erin = Member.objects.create(first_name='Erin')
        john = Member.objects.create(first_name='John')
        steve = Member.objects.create(first_name='Steve')

        # Add platform team members to groups
        osf_platform_managers.add_member(casey)
        osf_platform_managers.add_member(steve)

        osf_platform_members.add_member(casey)
        osf_platform_members.add_member(dawn)
        osf_platform_members.add_member(erin)
        osf_platform_members.add_member(john)
        osf_platform_members.add_member(steve)

        # Casey and Steve can manage both the member and manager groups
        self.assertTrue(casey.has_perm('manage_group', osf_platform_managers))
        self.assertTrue(casey.has_perm('manage_group', osf_platform_members))
        self.assertTrue(steve.has_perm('manage_group', osf_platform_managers))
        self.assertTrue(steve.has_perm('manage_group', osf_platform_members))

        # Erin, John, and I can't manage the member or manager groups
        self.assertFalse(dawn.has_perm('manage_group', osf_platform_managers))
        self.assertFalse(dawn.has_perm('manage_group', osf_platform_members))
        self.assertFalse(erin.has_perm('manage_group', osf_platform_managers))
        self.assertFalse(erin.has_perm('manage_group', osf_platform_members))
        self.assertFalse(john.has_perm('manage_group', osf_platform_managers))
        self.assertFalse(john.has_perm('manage_group', osf_platform_members))

    def test_osf_groups_resource_assignment_via_group_type_permissions(self):
        # OSF Group
        platform_team = Group.objects.create(name='Platform Team')

        # Group member roles
        manager = GroupMemberRole.objects.create(label='group manager')
        member = GroupMemberRole.objects.create(label='group member')

        # Members
        casey = Member.objects.create(first_name='Casey')
        dawn = Member.objects.create(first_name='Dawn')
        erin = Member.objects.create(first_name='Erin')
        john = Member.objects.create(first_name='John')
        steve = Member.objects.create(first_name='Steve')

        # Add to platform team
        platform_team.add_member(casey, [manager])
        platform_team.add_member(steve, [manager])
        platform_team.add_member(erin, [member])
        platform_team.add_member(john, [member])
        platform_team.add_member(dawn, [member])

        # Create manage group permission
        content_type = ContentType.objects.get_for_model(Group)
        manage_permission = Permission.objects.create(
            codename='manage_group',
            name='Can manage group membership',
            content_type=content_type
        )

        custom_permissions = {
            'owner': {
                'group-manager': ['manage_group'],
            }
        }

        # Looks like for roles you have to assign permission to user instead of group
        casey.assign_object(platform_team, platform_team, custom_permissions=custom_permissions)
        steve.assign_object(platform_team, platform_team, custom_permissions=custom_permissions)
        dawn.assign_object(platform_team, platform_team, custom_permissions=custom_permissions)
        erin.assign_object(platform_team, platform_team, custom_permissions=custom_permissions)
        john.assign_object(platform_team, platform_team, custom_permissions=custom_permissions)

        self.assertTrue(casey.has_perm('manage_group', platform_team))
        self.assertTrue(steve.has_perm('manage_group', platform_team))
        self.assertFalse(dawn.has_perm('manage_group', platform_team))
        self.assertFalse(erin.has_perm('manage_group', platform_team))
        self.assertFalse(john.has_perm('manage_group', platform_team))


    def test_members_can_link_to_users(self):
        bob = User.objects.create_user(username='bob', first_name='bob', email='bob@tom.io', password='testpassword')
        tom = User.objects.create_user(username='tom', first_name='tom', email='tom@bob.io', password='testpassword')
        # django_user is defined in AUTH_USER_MODEL
        bob_member = Member.objects.create(django_user=bob)
        tom_member = Member.objects.create(django_user=tom)

        self.assertTrue(bob_member.django_user_id, bob.id)
        self.assertTrue(tom_member.django_user_id, tom.id)
