FIELD_TYPE_MAP = {
    'CharField': 'text',
    'DateTimeField': 'dateTime',
    'IntegerField': 'digit',
    'TextField': 'textarea',
}

def _get_foreign_key_enums(field):
        """获取ForeignKey字段的enums
        """
        for obj in field.model.objects.all():
            related_pk = getattr(obj, field.name).pk
            related_obj = field.related_model.objects.get(pk=related_pk)
            yield str(related_obj.pk), str(related_obj)


def _get_many_to_many_enums(field):
    """获取ManyToMany字段的enums
    """
    for obj in field.related_model.objects.all():
        yield str(obj.pk), str(obj)


def _get_select_field(self, field):
    # 先获取过滤后的queryset
    filtered_queryset = self.filter_queryset(self.queryset)
    # 再获取field字段上的所有值
    value_list = list(filtered_queryset.values_list(field.name, flat=True).distinct())
    value_enum = {
        str(v): {'text': v} for v in value_list
    }
    return {'valueEnum': value_enum, 'valueType': 'select', 'filters': True}


def handle_field_name(self, field, column):
    select_fields = getattr(self, 'select_fields', [])
    sorter_fields = getattr(self, 'sorter_fields', [])
    copyable_fields = getattr(self, 'copyable_fields', [])
    not_search_fields = getattr(self, 'not_search_fields', [])
    hidden_fields = getattr(self, 'hidden_fields', [])
    render_region_fields = getattr(self, 'render_region_fields', [])
    render_compare_fields = getattr(self, 'render_compare_fields', [])
    
    if field.name in select_fields:
        column.update(_get_select_field(self, field))

    if field.name in sorter_fields:
        column['sorter'] = True

    if field.name in copyable_fields:
        column['copyable'] = True

    if field.name in not_search_fields:
        column['search'] = False

    if field.name in hidden_fields:
        column['hideInTable'] = True
        column['search'] = False

    if field.name in render_region_fields:
        column['render_region'] = True

    if field.name in render_compare_fields:
        column['render_compare'] = True

    if field.name == 'password':
        column['valueType'] = 'password'


def handle_value_type(field, value_type, column):
    # 外键关联字段和多对多字段，应获取相应的select
    if value_type in ('ForeignKey', 'ManyToManyField'):
        if value_type == 'ForeignKey':
            value_enum = dict(_get_foreign_key_enums(field))
        else:
            value_enum = dict(_get_many_to_many_enums(field))
        column['valueType'] = 'select'
        column['valueEnum'] = value_enum
        column['filters'] = True

        if value_type == 'ManyToManyField':
            column['fieldProps'] = {'mode': 'multiple'}

    # BooleanField处理
    if value_type == 'BooleanField':
        column['valueType'] = 'switch'
        column['fieldProps'] = {'checkedChildren': '是', 'unCheckedChildren': '否'}


def get_columns_data(self):
    data = []

    serializer_fields = self.get_serializer().fields  # 去除了exclude字段

    # fields = self.queryset.model._meta.fields  # 不包含ManyToMany字段
    fields = self.queryset.model._meta.get_fields()

    verbose_name_map = getattr(self, 'verbose_name_map', {})
    field_type_map = {**FIELD_TYPE_MAP, **getattr(self, 'field_type_map', {})}

    for field in fields:
        if field.name not in serializer_fields:
            continue

        field_type = field.get_internal_type()
        
        value_type = field_type_map.get(field_type, field_type)
        title = verbose_name_map.get(field.name, field.verbose_name)
        column = {
            'key': field.name,
            'dataIndex': field.name,
            'title': title,
            'valueType': value_type,
        }

        if serializer_fields.get(field.name).read_only:
            column['editable'] = False

        handle_field_name(self, field, column)
        handle_value_type(field, value_type, column)

        data.append(column)
        
    return data
