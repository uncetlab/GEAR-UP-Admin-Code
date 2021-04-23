"""
    mixin
    ~~~~~

    Mixins for views (admin and cbv) for django-reversion-compare

    :copyleft: 2012-2015 by the django-reversion-compare team,
     see AUTHORS for more details.
    :license: GNU GPL v3 or above, see LICENSE for more details.
"""
import django
import difflib

from django.db import models
from django.template.loader import render_to_string
from django.utils.encoding import force_text

import logging

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext as _

from reversion import is_registered
from reversion.models import Version
from reversion.revisions import _get_options

from django.contrib import admin
from django.contrib.admin.sites import NotRegistered
from django.utils.html import escape
from django.utils.safestring import mark_safe

logger = logging.getLogger(__name__)


try:
    # http://code.google.com/p/google-diff-match-patch/
    from diff_match_patch import diff_match_patch
except ImportError:
    dmp = None
else:
    dmp = diff_match_patch()


def highlight_diff(diff_text):
    """
    Simple highlight a diff text in the way pygments do it ;)
    """
    html = ['<pre class="highlight">']
    for line in diff_text.splitlines():
        line = escape(line)
        if line.startswith("+"):
            line = f"<ins>{line}</ins>"
        elif line.startswith("-"):
            line = f"<del>{line}</del>"

        html.append(line)
    html.append("</pre>")
    html = "\n".join(html)

    return html


SEMANTIC = 1
EFFICIENCY = 2

# Change from ndiff to unified_diff if old/new values are more than X lines:
LINE_COUNT_4_UNIFIED_DIFF = 4


def unified_diff(a, b, n=3, lineterm="\n"):
    r"""
    simmilar to the original difflib.unified_diff except:
        - no fromfile/tofile and no fromfiledate/tofiledate info lines
        - newline before diff control lines and not after

    Example:

    >>> for line in unified_diff('one two three four'.split(),
    ...             'zero one tree four'.split(), lineterm=''):
    ...     print(line)
    @@ -1,4 +1,4 @@
    +zero
     one
    -two
    -three
    +tree
     four
    """
    started = False
    for group in difflib.SequenceMatcher(None, a, b).get_grouped_opcodes(n):
        first, last = group[0], group[-1]
        file1_range = difflib._format_range_unified(first[1], last[2])
        file2_range = difflib._format_range_unified(first[3], last[4])

        if not started:
            started = True
            yield f"@@ -{file1_range} +{file2_range} @@"
        else:
            yield f"{lineterm}@@ -{file1_range} +{file2_range} @@"

        for tag, i1, i2, j1, j2 in group:
            if tag == "equal":
                for line in a[i1:i2]:
                    yield " " + line
                continue
            if tag in ("replace", "delete"):
                for line in a[i1:i2]:
                    yield "-" + line
            if tag in ("replace", "insert"):
                for line in b[j1:j2]:
                    yield "+" + line


def html_diff(value1, value2, cleanup=SEMANTIC):
    """
    Generates a diff used google-diff-match-patch is exist or ndiff as fallback

    The cleanup parameter can be SEMANTIC,
    EFFICIENCY or None to clean up the diff
    for greater human readibility.
    """
    value1 = force_text(value1)
    value2 = force_text(value2)
    if dmp is not None:
        # Generate the diff with google-diff-match-patch
        diff = dmp.diff_main(value1, value2)
        if cleanup == SEMANTIC:
            dmp.diff_cleanupSemantic(diff)
        elif cleanup == EFFICIENCY:
            dmp.diff_cleanupEfficiency(diff)
        elif cleanup is not None:
            raise ValueError(
                "cleanup parameter should be one of SEMANTIC,\
                EFFICIENCY or None.")
        html = dmp.diff_prettyHtml(diff)
        html = html.replace("&para;<br>", "</br>")
    else:
        # fallback: use built-in difflib
        value1 = value1.splitlines()
        value2 = value2.splitlines()

        if len(value1) > LINE_COUNT_4_UNIFIED_DIFF or \
                len(value2) > LINE_COUNT_4_UNIFIED_DIFF:
            diff = unified_diff(value1, value2, n=2)
        else:
            diff = difflib.ndiff(value1, value2)

        diff_text = "\n".join(diff)
        html = highlight_diff(diff_text)

    html = mark_safe(html)

    return html


# def compare_queryset(first, second):
#     """
#     Simple compare two querysets (used for many-to-many field compare)
#     XXX: resort results?
#     """
#     result = []
#     for item in set(first).union(set(second)):
#         if item not in first:  # item was inserted
#             item.insert = True
#         elif item not in second:  # item was deleted
#             item.delete = True
#         result.append(item)
#     return result


# def patch_admin(model, admin_site=None, AdminClass=None, skip_non_revision=False):
#     """
#     Enables version control with full admin integration for a model that has
#     already been registered with the django admin site.

#     This is excellent for adding version control to existing Django contrib
#     applications.

#     :param skip_non_revision: If ==True: Skip models that are not register with ModelAdmin
#     """
#     admin_site = admin_site or admin.site
#     try:
#         ModelAdmin = admin_site._registry[model].__class__
#     except KeyError:
#         raise NotRegistered(f"The model {model} has not been registered with the admin site.")

#     if skip_non_revision:
#         if not hasattr(ModelAdmin, "object_history_template"):
#             logger.info(
#                 "Skip activate compare admin, because model %r is not registered with revision manager."
#                 % model._meta.object_name
#             )
#         return

#     # Unregister existing admin class.
#     admin_site.unregister(model)

#     # Register patched admin class.
#     if not AdminClass:
#         from reversion_compare.admin import CompareVersionAdmin

#         class PatchedModelAdmin(CompareVersionAdmin, ModelAdmin):
#             pass

#     else:

#         class PatchedModelAdmin(AdminClass, ModelAdmin):
#             pass

#     admin_site.register(model, PatchedModelAdmin)


# if __name__ == "__main__":
#     import doctest

#     print(
#         doctest.testmod(
#             verbose=False
#             # verbose=True
#         )
#     )

class FieldVersionDoesNotExist:
    """
    Sentinel object to handle missing fields
    """

    def __str__(self):
        return force_text(_("Field didn't exist!"))


DOES_NOT_EXIST = FieldVersionDoesNotExist()


class CompareObject:
    def __init__(self, field, field_name, obj, version_record, follow):
        self.field = field
        self.field_name = field_name
        self.obj = obj
        self.version_record = version_record
        self.follow = follow
        # try and get a value, if none punt
        self.compare_foreign_objects_as_id = getattr(
            settings, "REVERSION_COMPARE_FOREIGN_OBJECTS_AS_ID", False)
        # ignore not registered models
        self.ignore_not_registered = getattr(
            settings, "REVERSION_COMPARE_IGNORE_NOT_REGISTERED", False)
        if self.compare_foreign_objects_as_id:
            self.value = version_record.field_dict.get(
                getattr(field, "attname", field_name), DOES_NOT_EXIST)
        else:
            self.value = version_record.field_dict.get(
                field_name, DOES_NOT_EXIST)

    def _obj_repr(self, obj):
        # FIXME: How to create a better representation of the current value?
        try:
            return force_text(obj)
        except Exception:
            return repr(obj)

    def _choices_repr(self, obj):
        return force_text(
            dict(self.field.flatchoices).get(obj, obj), strings_only=True)

    # def _to_string_ManyToManyField(self):
    #     return ", ".join(
    #         self._obj_repr(item) for item in self.get_many_to_many())

    # def _to_string_ForeignKey(self):
    #     return self._obj_repr(self.get_related())

    def to_string(self):
        internal_type = self.field.get_internal_type()
        func_name = f"_to_string_{internal_type}"
        if hasattr(self, func_name):
            func = getattr(self, func_name)
            return func()

        if hasattr(self.field, 'choices') and self.field.choices:
            return self._choices_repr(self.value)

        if isinstance(self.value, str):
            return self.value
        else:
            return self._obj_repr(self.value)

    def __cmp__(self, other):
        raise NotImplementedError

    def __eq__(self, other):
        if hasattr(self.field, "get_internal_type"):
            assert self.field.get_internal_type() != "ManyToManyField"

        if self.value != other.value:
            return False

        # see - https://hynek.me/articles/hasattr/
        if not self.compare_foreign_objects_as_id:
            internal_type = getattr(self.field, "get_internal_type", None)
            if internal_type is None or \
                    internal_type() == "ForeignKey":  # FIXME!
                if self.version_record.field_dict != \
                        other.version_record.field_dict:
                    return False

        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def get_object_version(self):
        if hasattr(self.version_record, "_object_version"):
            return getattr(self.version_record, "_object_version")
        else:
            return getattr(self.version_record, "object_version")

    def get_related(self):
        if getattr(self.field, "related_model", None):
            obj = self.get_object_version().object
            try:
                return getattr(obj, self.field.name, None)
            except ObjectDoesNotExist:
                return None

    def get_reverse_foreign_key(self):
        obj = self.get_object_version().object
        if self.field.related_name and hasattr(obj, self.field.related_name):
            if isinstance(self.field, models.fields.related.OneToOneRel):
                try:
                    ids = {force_text(getattr(obj, force_text(
                        self.field.related_name)).pk)}
                except ObjectDoesNotExist:
                    ids = set()
            else:
                ids = {force_text(v.pk) for v in getattr(
                    obj, force_text(self.field.related_name)).all()}
                if not ids and any(
                    [f.name.endswith("_ptr")
                     for f in obj._meta.get_fields()]):
                    others = self.version_record.revision.version_set.filter(
                        object_id=self.version_record.object_id
                    ).all()
                    for p in others:
                        if hasattr(p, "_object_version"):
                            p_obj = getattr(p, "_object_version").object
                        else:
                            p_obj = getattr(p, "object_version").object
                        if not isinstance(p_obj, type(obj)) \
                                and hasattr(
                                p_obj, force_text(self.field.related_name)):
                            ids = {force_text(v.pk) for v in getattr(p_obj,
                                force_text(self.field.related_name)).all()}
        else:
            return {}, {}, []  # TODO: refactor that

        # Get the related model of the current field:
        related_model = self.field.field.model
        return self.get_many_to_something(ids, related_model, is_reverse=True)

    def get_many_to_many(self):
        """
        returns a queryset with all many2many objects
        """
        if self.field.get_internal_type() != "ManyToManyField":  # FIXME!
            return {}, {}, []  # TODO: refactor that
        elif self.value is DOES_NOT_EXIST:
            return {}, {}, []  # TODO: refactor that

        try:
            ids = frozenset(map(force_text, self.value))
        except TypeError:
            # catch errors e.g. produced by taggit's TaggableManager
            logger.exception("Can't collect m2m ids")
            return {}, {}, []  # TODO: refactor that

        # Get the related model of the current field:
        return self.get_many_to_something(ids, self.field.related_model)

    def get_many_to_something(self, target_ids, related_model, is_reverse=False):
        # get instance of reversion.models.Revision():
        # A group of related object versions.
        old_revision = self.version_record.revision

        # Get a queryset with all related objects.
        versions = {
            ver.object_id: ver
            for ver in old_revision.version_set.filter(
                content_type=ContentType.objects.get_for_model(related_model), object_id__in=target_ids
            ).all()
        }

        missing_objects_dict = {}
        deleted = []

        if not self.follow:
            # This models was not registered with follow relations
            # Try to fill missing related objects
            potentially_missing_ids = target_ids.difference(frozenset(versions))
            # logger.debug(
            #     self.field_name,
            #     f"target: {target_ids} - actual: {versions} - missing: {potentially_missing_ids}"
            # )
            if potentially_missing_ids:
                missing_objects_dict = {
                    force_text(rel.pk): rel
                    for rel in related_model.objects.filter(pk__in=potentially_missing_ids).iterator()
                    if is_registered(rel.__class__) or not self.ignore_not_registered
                }

        if is_reverse:
            missing_objects_dict = {
                ver.object_id: ver
                for o in missing_objects_dict.values()
                for ver in Version.objects.get_for_object(o)
                if ver.revision.date_created < old_revision.date_created
            }

            if is_registered(related_model) or not self.ignore_not_registered:
                # shift query to database
                deleted = list(Version.objects.filter(revision=old_revision).get_deleted(related_model))
            else:
                deleted = []

        return versions, missing_objects_dict, deleted

    def get_debug(self):  # pragma: no cover
        if not settings.DEBUG:
            return

        result = [
            f"field..............: {self.field!r}",
            f"field_name.........: {self.field_name!r}",
            "field internal type: %r" % self.field.get_internal_type(),
            "field_dict.........: %s" % repr(self.version_record.field_dict),
            f"obj................: {self.obj!r} (pk: {self.obj.pk}, id: {id(self.obj)})",
            "version............: %r (pk: %s, id: %s)"
            % (self.version_record, self.version_record.pk, id(self.version_record)),
            f"value..............: {self.value!r}",
            "to string..........: %s" % repr(self.to_string()),
            "related............: %s" % repr(self.get_related()),
        ]
        m2m_versions, missing_objects, missing_ids, deleted = self.get_many_to_many()
        if m2m_versions or missing_objects or missing_ids:
            result.append(
                "many-to-many.......: %s" % ", ".join(f"{item} ({item.type})" for item in m2m_versions)
            )

            if missing_objects:
                result.append("missing m2m objects: %s" % repr(missing_objects))
            else:
                result.append("missing m2m objects: (has no)")

            if missing_ids:
                result.append("missing m2m IDs....: %s" % repr(missing_ids))
            else:
                result.append("missing m2m IDs....: (has no)")
        else:
            result.append("many-to-many.......: (has no)")

        return result

    # def debug(self):  # pragma: no cover
    #     if not settings.DEBUG:
    #         return
    #     for item in self.get_debug():
    #         logger.debug(item)


class CompareObjects:
    def __init__(self, field, field_name, obj, version1, version2, is_reversed):
        self.field = field
        self.field_name = field_name
        self.obj = obj

        # is a related field (ForeignKey, ManyToManyField etc.)
        self.is_related = getattr(self.field, "related_model", None) is not None
        self.is_reversed = is_reversed
        if not self.is_related:
            self.follow = None
        elif self.field_name in _get_options(self.obj.__class__).follow:
            self.follow = True
        else:
            self.follow = False

        self.compare_obj1 = CompareObject(field, field_name, obj, version1, self.follow)
        self.compare_obj2 = CompareObject(field, field_name, obj, version2, self.follow)

        self.value1 = self.compare_obj1.value
        self.value2 = self.compare_obj2.value

        self.M2O_CHANGE_INFO = None
        self.M2M_CHANGE_INFO = None

    def changed(self):
        """ return True if at least one field has changed values. """

        info = None
        if hasattr(self.field, "get_internal_type") and self.field.get_internal_type() == "ManyToManyField":
            info = self.get_m2m_change_info()
        elif self.is_reversed:
            info = self.get_m2o_change_info()
        if info:
            keys = (
                "changed_items",
                "removed_items",
                "added_items",
                "removed_missing_objects",
                "added_missing_objects",
                "deleted_items",
            )
            for key in keys:
                if info[key]:
                    return True
            return False

        return self.compare_obj1 != self.compare_obj2

    def to_string(self):
        return self.compare_obj1.to_string(), self.compare_obj2.to_string()

    def get_related(self):
        return self.compare_obj1.get_related(), self.compare_obj2.get_related()

    def get_many_to_many(self):
        return self.compare_obj1.get_many_to_many(), self.compare_obj2.get_many_to_many()

    def get_reverse_foreign_key(self):
        return self.compare_obj1.get_reverse_foreign_key(), self.compare_obj2.get_reverse_foreign_key()

    def get_m2o_change_info(self):
        if self.M2O_CHANGE_INFO is not None:
            return self.M2O_CHANGE_INFO

        m2o_data1, m2o_data2 = self.get_reverse_foreign_key()

        self.M2O_CHANGE_INFO = self.get_m2s_change_info(m2o_data1, m2o_data2)
        return self.M2O_CHANGE_INFO

    def get_m2m_change_info(self):
        if self.M2M_CHANGE_INFO is not None:
            return self.M2M_CHANGE_INFO

        m2m_data1, m2m_data2 = self.get_many_to_many()

        self.M2M_CHANGE_INFO = self.get_m2s_change_info(m2m_data1, m2m_data2)
        return self.M2M_CHANGE_INFO

    # Abstract Many-to-Something (either -many or -one) as both
    # many2many and many2one relationships looks the same from the referred object.
    def get_m2s_change_info(self, obj1_data, obj2_data):

        result_dict1, missing_objects_dict1, deleted1 = obj1_data
        result_dict2, missing_objects_dict2, deleted2 = obj2_data

        # Create same_items, removed_items, added_items with related m2m items
        changed_items = []
        removed_items = []
        added_items = []
        same_items = []

        same_missing_objects_dict = {k: v for k, v in missing_objects_dict1.items() if k in missing_objects_dict2}
        removed_missing_objects_dict = {
            k: v for k, v in missing_objects_dict1.items() if k not in missing_objects_dict2
        }
        added_missing_objects_dict = {k: v for k, v in missing_objects_dict2.items() if k not in missing_objects_dict1}

        # logger.debug("same_missing_objects: %s", same_missing_objects_dict)
        # logger.debug("removed_missing_objects: %s", removed_missing_objects_dict)
        # logger.debug("added_missing_objects: %s", added_missing_objects_dict)

        for primary_key in set().union(result_dict1.keys(), result_dict2.keys()):
            if primary_key in result_dict1:
                version1 = result_dict1[primary_key]
            else:
                version1 = None

            if primary_key in result_dict2:
                version2 = result_dict2[primary_key]
            else:
                version2 = None

            # logger.debug("%r - %r - %r", primary_key, version1, version2)

            if version1 is not None and version2 is not None:
                # In both -> version changed or the same
                if version1.serialized_data == version2.serialized_data:
                    # logger.debug("same item: %s", version1)
                    same_items.append(version1)
                else:
                    changed_items.append((version1, version2))
            elif version1 is not None and version2 is None:
                # In 1 but not in 2 -> removed
                # logger.debug("%s %s", primary_key, missing_objects_dict2)
                # logger.debug("%s %s", repr(primary_key), repr(missing_objects_dict2))
                if primary_key in added_missing_objects_dict:
                    added_missing_objects_dict.pop(primary_key)
                    same_missing_objects_dict[primary_key] = missing_objects_dict2[primary_key]
                    continue
                removed_items.append(version1)
            elif version1 is None and version2 is not None:
                # In 2 but not in 1 -> added
                # logger.debug("added: %s", version2)
                added_items.append(version2)
            else:
                raise RuntimeError()

        # In Place Sorting of Lists (exclude changed since its a tuple)
        removed_items.sort(key=lambda item: force_text(item))
        added_items.sort(key=lambda item: force_text(item))
        same_items.sort(key=lambda item: force_text(item))
        deleted1.sort(key=lambda item: force_text(item))
        same_missing_objects = sorted(same_missing_objects_dict.values(), key=lambda item: force_text(item))
        removed_missing_objects = sorted(removed_missing_objects_dict.values(), key=lambda item: force_text(item))
        added_missing_objects = sorted(added_missing_objects_dict.values(), key=lambda item: force_text(item))

        return {
            "changed_items": changed_items,
            "removed_items": removed_items,
            "added_items": added_items,
            "same_items": same_items,
            "same_missing_objects": same_missing_objects,
            "removed_missing_objects": removed_missing_objects,
            "added_missing_objects": added_missing_objects,
            "deleted_items": deleted1,
        }


class CompareMixin:
    """A mixin to add comparison capabilities to your views"""

    # list/tuple of field names for the compare view. Set to None for all existing fields
    compare_fields = None

    # list/tuple of field names to exclude from compare view.
    compare_exclude = ['modified', 'invited_date','updated', 'created', 'university']

    # sort from new to old as default, see: https://github.com/etianen/django-reversion/issues/77
    history_latest_first = True

    def _order_version_queryset(self, queryset):
        """Applies the correct ordering to the given version queryset."""
        if self.history_latest_first:
            return queryset.order_by("-pk")
        return queryset.order_by("pk")

    def _get_compare(self, obj_compare):
        """
        Call the methods to create the compare html part.
        Try:
            1. name scheme: "compare_%s" % field_name
            2. name scheme: "compare_%s" % field.get_internal_type()
            3. Fallback to: self.fallback_compare()
        """

        def _get_compare_func(suffix):
            # logger.debug("func_name: %s", func_name)
            func_name = f"compare_{suffix}"
            if hasattr(self, func_name):
                func = getattr(self, func_name)
                if callable(func):
                    return func

        # Try method in the name scheme: "compare_%s" % field_name
        func = _get_compare_func(obj_compare.field_name)
        if func is not None:
            html = func(obj_compare)
            return html

        # Determine if its a reverse field
        if obj_compare.field in self.reverse_fields:
            func = _get_compare_func("ManyToOneRel")
            if func is not None:
                html = func(obj_compare)
                return html

        # Try method in the name scheme: "compare_%s" % field.get_internal_type()
        internal_type = obj_compare.field.get_internal_type()
        func = _get_compare_func(internal_type)
        if func is not None:
            html = func(obj_compare)
            return html

        # Fallback to self.fallback_compare()
        html = self.fallback_compare(obj_compare)
        return html

    def compare(self, obj, version1, version2):
        """
        Create a generic html diff from the obj between version1 and version2:

            A diff of every changes field values.

        This method should be overwritten, to create a nice diff view
        coordinated with the model.
        """
        diff = []

        # Create a list of all normal fields and append many-to-many fields
        fields = [field for field in obj._meta.fields]
        concrete_model = obj._meta.concrete_model
        fields += concrete_model._meta.many_to_many

        # This gathers the related reverse ForeignKey fields, so we can do ManyToOne compares
        if django.VERSION < (1, 10):
            # From: http://stackoverflow.com/questions/19512187/django-list-all-reverse-relations-of-a-model
            self.reverse_fields = []
            for field_name in obj._meta.get_all_field_names():
                f = getattr(obj._meta.get_field_by_name(field_name)[0], "field", None)
                if isinstance(f, models.ForeignKey) and f not in fields:
                    self.reverse_fields.append(f.rel)
        else:
            # django >= v1.10
            self.reverse_fields = []
            for field in obj._meta.get_fields(include_hidden=True):
                f = getattr(field, "field", None)
                if isinstance(f, models.ForeignKey) and f not in fields:
                    self.reverse_fields.append(f.remote_field)

        fields += self.reverse_fields

        has_unfollowed_fields = False

        for field in fields:
            # logger.debug("%s %s %s", field, field.db_type, field.get_internal_type())
            try:
                field_name = field.name
            except BaseException:
                # is a reverse FK field
                field_name = field.field_name

            if self.compare_fields and field_name not in self.compare_fields:
                continue
            if self.compare_exclude and field_name in self.compare_exclude:
                continue

            is_reversed = field in self.reverse_fields
            obj_compare = CompareObjects(field, field_name, obj, version1, version2, is_reversed)
            # obj_compare.debug()

            is_related = obj_compare.is_related
            follow = obj_compare.follow
            if is_related and not follow:
                has_unfollowed_fields = True

            if not obj_compare.changed():
                # Skip all fields that aren't changed
                continue

            html = self._get_compare(obj_compare)
            diff.append({"field": field, "is_related": is_related, "follow": follow, "diff": html})

        return diff, has_unfollowed_fields

    def fallback_compare(self, obj_compare):
        """
        Simply create a html diff from the repr() result.
        Used for every field which has no own compare method.
        """
        value1, value2 = obj_compare.to_string()
        html = html_diff(value1, value2)
        return html