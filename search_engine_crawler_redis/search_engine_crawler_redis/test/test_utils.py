from unittest import TestCase

from utils import search_contact_us


class TestUtils(TestCase):

    def test_search_contact_us(self):
        text = '<a href="zhaoshang.asp" class="link2">留言反馈</a>&nbsp;| ' \
               '<a href="contact.asp" class="link2">联系我们</a></td>' \
               '<a href="us.jsp" class="link2">ContactUs</a></td>'

        result = search_contact_us(text)

        self.assertEqual(result, ['contact.asp', 'us.jsp'])
