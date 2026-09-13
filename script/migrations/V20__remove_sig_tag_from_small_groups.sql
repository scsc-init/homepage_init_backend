BEGIN;

-- Remove only the SIG association from groups that also have the 소모임 tag.
DELETE FROM public.sig_tag AS sig_link
USING public.tag AS sig_tag
WHERE sig_link.tag_id = sig_tag.id
  AND sig_tag.text = 'SIG'
  AND EXISTS (
      SELECT 1
      FROM public.sig_tag AS small_group_link
      JOIN public.tag AS small_group_tag
        ON small_group_tag.id = small_group_link.tag_id
      WHERE small_group_link.sig_id = sig_link.sig_id
        AND small_group_tag.text = '소모임'
  );

COMMIT;
