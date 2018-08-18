from django.test import TestCase

from groups_manager.models import Group, GroupType, Member

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

        # Attach Node Groups to Node Objects (w/ implicit upstream view/read)
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

        # Verify Explicit Admin Permission
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
