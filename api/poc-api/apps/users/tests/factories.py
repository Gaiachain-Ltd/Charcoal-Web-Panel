# -*- coding: utf-8 -*-
import factory


class RoleFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: 'role-{0}'.format(n))

    class Meta:
        model = 'users.Role'
        django_get_or_create = ('name', )


class UserFactory(factory.django.DjangoModelFactory):
    email = factory.Sequence(lambda n: 'user-{0}@example.com'.format(n))
    password = factory.PostGenerationMethodCall('set_password', 'password')
    role = factory.SubFactory(RoleFactory)

    class Meta:
        model = 'users.User'
        django_get_or_create = ('email',)
