from aoty.aotyparser import AotyListsListsParser


input_file = open('input/input_lists_lists.txt', mode='r', encoding="utf-8")
error_file = open('errors/errors_lists_lists.txt', mode='w', encoding="utf-8")
output_file = open('output/output_lists_lists.txt', mode='w', encoding="utf-8")
parser = AotyListsListsParser()
for l in input_file:
    line = l.replace('\n', '')
    if (line != ""):
        try:
            critic, lists_link = line.split('\t')
            lists = parser.get_lists_by_critic(lists_link)
            for l in lists:
                output_file.write(f"{critic}"
                                  f"\t{critic} - {l['list_name']}"
                                  f"\t{l['list_label']}"
                                  f"\t{l['aoty_link']}"
                                  f"\t{l['original_link']}"
                                  f"\n")
        except Exception as e:
            error_file.write('{line}\t{e}\n'.format(line=line, e=e))

#   free the resources
input_file.close()
output_file.close()
error_file.close()
