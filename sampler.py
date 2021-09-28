import sys
import json
import random
from pprint import pprint
from data_loading_functions import JSONLoader, JSONSaver, TEXTLoader, TEXTSaver
from params import Parameters


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
        return self.load_data()

    def load_data(self):
        loader = TEXTLoader(self.f_data)
        lines = loader().split("\n")
        doc_name2data = dict()
        for idx, line in enumerate(lines):
            line = line.replace("@@ ", "")
            if line.strip():
                pass
            else:
                continue
            converted = self.text_line_to_readable_dict(line)
            key_ = converted['doc_name']
            if key_ in doc_name2data:
                doc_name2data[key_].append(converted)
            else:
                doc_name2data[key_] = [converted]

        if Parameters.save_to_file:
            saver = JSONSaver(doc_name2data, self.f_save)
            saver()
        
        return doc_name2data

    def frequency_measure_tag_and_values(self):
        """
        This functions print out the info on tag and value frequencies in the CLI terminal 
        and save the info into the txt files within the working directory.

        Args:
            None

        Returns:
            None
        """

        doc_name2data = self.load_data()

        tag_dict = dict()
        value_dict = dict()

        for doc_name, basket_list in doc_name2data.items():
            for basket in basket_list:
                tags = [x['tag'] for x in basket['tag_value_list']]
                values = [x['value'] for x in basket['tag_value_list']]
                for tag_ in tags:
                    if tag_ in tag_dict:
                        tag_dict[tag_] += 1
                    else:
                        tag_dict[tag_] = 1
                for value_ in values:
                    if value_ in value_dict:
                        value_dict[value_] += 1
                    else:
                        value_dict[value_] = 1

        tag_list = list(tag_dict.keys())
        value_list = list(value_dict.keys())

        tag_list = sorted(tag_list, key = lambda x: tag_dict[x], reverse=True)
        value_list = sorted(value_list, key = lambda x: value_dict[x], reverse=True)
        
        tag_save_text = ""
        value_save_text = ""
        
        for tag_ in tag_list:
            tag_save_text += "\t".join([tag_, str(tag_dict[tag_])])
            tag_save_text += "\n"

        for value_ in value_list:
            value_save_text += "\t".join([value_, str(value_dict[value_])]) 
            value_save_text += "\n"

        tag_saver = TEXTSaver(tag_save_text, f"tag_frequency_{self.f_tail}.txt") 
        tag_saver()
        value_saver = TEXTSaver(value_save_text, f"value_frequency_{self.f_tail}.txt") 
        value_saver()

        print("[File Saved] tag and value frequency list")
        print("-"*30)
        print(self.f_data)
        print("-"*30)
        print('#tags:', len(tag_list))
        print('tag_samples:', tag_list[:10])
        print("-"*30)
        print('#values:', len(value_list))
        print('value_sampes:', value_list[:10])
        print("-"*30)

        return

    def intersection_between_text_and_tag(self):
        # text = 


        return

    def text_line_to_readable_dict(self, line):
        basket = json.loads(line.strip())
        return self._dict_to_readable_dict(basket)

    def _dict_to_readable_dict(self, basket):
        tag_value_list = basket['data']
        tag_value_list = [{'tag': x[0], 'value': x[1]} for x in tag_value_list]
        doc_name = basket['doc_title']
        section_name = basket['sec_title']
        text = basket['text']
        to_return = {
            'doc_name': doc_name,
            'section_name': section_name,
            'tag_value_list': tag_value_list,
            'text': text,
        }
        return to_return

    def generate_parlai_data(self, basket):
        """
        Args:
            basket: dict, that has keys of
            'doc_name', 'section_name', 'tag_value_list', and 'text'
        
        Returns:
           a str, which is the parlai-format line, that contains
           'text:', 'labels:', 'label_candidates:', and 'episode_done:True'
        """
        # START FROM HERE
        pass


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
        to_return = {
            'doc_name': doc_name,
            'tag_value_list': tag_value_list
        }
        return to_return


class InfoBoxSampler(Sampler):
    def __init__(self):
        super().__init__('infobox')

    def _dict_to_readable_dict(self, basket):
        tag_value_list = []
        for tag_, val_ in basket['infobox'].items():
            tag_value_list.append({
                    'tag': tag_,
                    'value': val_
                })
        doc_name = basket['title']
        to_return = {
            'doc_name': doc_name,
            'tag_value_list': tag_value_list
        }
        return to_return

def data_compare():
    type2data = dict()
    for data_type in ['train', 'dev', 'test']:
        sampler = Sampler(data_type)
        type2data[data_type] = sampler()

    wiki_sampler = WikiSampler()
    type2data['wikidata'] = wiki_sampler()

    info_sampler = InfoBoxSampler()
    type2data['infobox'] = info_sampler()
    
    target_keys = list(type2data['infobox'].keys())
    random.shuffle(target_keys)
    target_keys = target_keys[:100]

    target_basket_dict = dict()
    for target_key in target_keys:
        target_basket = {}
        for type_, data_ in type2data.items():
            if target_key in data_:
                target_basket[type_] = data_[target_key]
            else:
                target_basket[type_] = []
        target_basket_dict[target_key] = target_basket
    saver = JSONSaver(target_basket_dict, "./chosen_samples.json")
    saver()
    return

def parlai_data_create():
    # START FROM HERE - CREATE A NEW DIRECTORY ON PARLAI-TASK
    # BASED ON THE 'LIGHT' PROJECT
    
    # specifically, set parameters on params.Parameters
    pass


if __name__ == "__main__":
    for data_type in ['train', 'dev', 'test']:
        sampler = Sampler(data_type)
        sampler.frequency_measure_tag_and_values()

