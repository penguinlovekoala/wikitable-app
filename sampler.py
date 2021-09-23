import sys
import json
from pprint import pprint
from data_loading_functions import JSONLoader, JSONSaver, TEXTLoader, TEXTSaver

class Sampler:
    def __init__(self, data_type):
        """
        Args:
            data_type: a str, which is one of "train", "dev", and "test"

        Returns:
            None
        """
        self.data_dir = "../data/final_data/"
        self.save_dir = "../data/converted/"
        self.f_tail = f"{data_type}.json"
        self.f_data = self.data_dir + self.f_tail
        self.f_save = self.save_dir + self.f_tail

    def __call__(self):
        loader = TEXTLoader(self.f_data)
        lines = loader().split("\n")
        converted_list = []
        for idx, line in enumerate(lines):
            if idx % 100000 == 0:
                print(f'at line {idx}')
            line = line.replace("@@ ", "")
            if line.strip():
                pass
            else:
                continue
            converted = self.text_line_to_readable_dict(line)
            converted_list.append(converted)
        saver = JSONSaver(converted_list, self.f_save)
        saver()

    def text_line_to_readable_dict(self, line):
        basket = json.loads(line.strip())
        return self._dict_to_readable_dict(basket)

    def _dict_to_readable_dict(self, basket):
        tag_value_list = basket['data']
        tag_value_list = [{'tag': x[0], 'value': x[1]} for x in tag_value_list]
        doc_name = basket['doc_title']
        section_name = basket['sec_title']
        text = basket['text']
        return {'doc_name': doc_name,
                'section_name': section_name,
                'tag_value_list': tag_value_list,
                'text': text,}


class WikiSampler(Sampler):
    def __init__(self):
        super().__init__('wikidata')

    def _dict_to_readable_dict(self, basket):
        tag_value_list = []
        for tag_, val_dict_list in basket['wikidata_details'].items():
            for val_dict in val_dict_list:
                val_ = val_dict['data'] 
                if isinstance(val_, str):
                    pass
                else:
                    continue
                tag_value_list.append({
                    'tag': tag_,
                    'value': val_
                })
        doc_name = basket['wikidata_name']
        return {'doc_name': doc_name,
                'tag_value_list': tag_value_list}


if __name__ == "__main__":
    # for data_type in ['train', 'dev', 'test']:
        # sampler = Sampler(data_type)
        # sampler()
    wiki_sampler = WikiSampler()
    # wiki_sampler()
