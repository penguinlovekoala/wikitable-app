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

        self.data_type = data_type
        self.data_dir = "../data/final_data/"
        self.save_dir = "../data/converted/"
        self.f_tail = f"{data_type}.json"
        self.f_data = self.data_dir + self.f_tail
        self.f_save = self.save_dir + self.f_tail

        self.set_num_basket_limit = Parameters.set_num_basket_limit
        if self.set_num_basket_limit:
            self.num_basket_limit = Parameters.num_basket_limit
        else:
            pass

    def __call__(self):
        return self.load_data()

    def load_data(self):
        """
        Args: None

        Returns:
            doc_name2data: dict where key is the doc_name and the value is the list of
                           basket where the basket is the dict that has keys of 'doc_name',
                           'section_name', 'tag_value_list', and 'text'
                           
        """
        loader = TEXTLoader(self.f_data)
        lines = loader().split("\n")
        doc_name2data = dict()
        for idx, line in enumerate(lines):
            line = line.replace("@@ ", "")
            if line.strip():
                pass
            else:
                continue

            if self.set_num_basket_limit:
                if idx > self.num_basket_limit:
                    break
                else:
                    pass
            else:
                pass

            converted = self.text_line_to_readable_dict(line)
            key_ = converted['doc_name']
            if key_ in doc_name2data:
                doc_name2data[key_].append(converted)
            else:
                doc_name2data[key_] = [converted]

        print("data_save:", self.data_type, "num_line:", idx)
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

        tag_list = sorted(tag_list, key=lambda x: tag_dict[x], reverse=True)
        value_list = sorted(value_list, key=lambda x: value_dict[x], reverse=True)
        
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
        doc_name2data = self.load_data()

        count_tags, count_values, count_intersection_tag, count_intersection_value \
            = 0, 0, 0, 0
        for doc_name, basket_list in doc_name2data.items():
            for basket in basket_list:
                text = basket["text"]
                tags = [x['tag'] for x in basket['tag_value_list']]
                values = [x['value'] for x in basket['tag_value_list']]

                num_tags = len(tags)
                num_values = len(values)

                num_tag_intersection = len([x for x in tags if x in text])
                num_value_intersection = len([x for x in values if x in text])
                
                count_tags += num_tags
                count_intersection_tag += num_tag_intersection

                count_values += num_values
                count_intersection_value += num_value_intersection

                for tag_ in tags:
                    if tag_ in text:
                        print("[TAGS]", tag_)
                    else:
                        pass

                print("-"*30)

                for value_ in values:
                    if value_ in values:
                        print("[VALUES]", value_)
                    else:
                        pass
                print("-"*30)
                print(text)
                sys.exit()

        print("-"*30)
        print(self.f_tail)
        print("-"*30)
        print("[count_tags, count_values, count_intersection_tag, count_intersection_value]")
        print(count_tags, count_values, count_intersection_tag, count_intersection_value)
        print("-"*30)


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

    def generate_parlai_data(self):
        """
        loaded data by the self.load_data() returns 
            doc_name2data: dict where key is the doc_name and
                           the value is the list of
                           basket where the basket is
                           the dict that has keys of
                           'doc_name', 'section_name',
                           'tag_value_list', and 'text'
        Args:
            None
        
        Returns:
           a str, which is the parlai-format line, that contains
           'text:', 'labels:', 'label_candidates:', and 'episode_done:True'
        """

        doc_name2data = self.load_data()

        parlai_lines = []
        for doc_name, basket_list in doc_name2data.items():
            for basket in basket_list:
                parlai_lines.append(
                    self.create_generation_lines_parlai(basket)
                )

        save_dir = f"{self.data_type}.txt"
        saver = TEXTSaver("\n".join(parlai_lines), save_dir)
        saver()

        print("-"*30)
        print(f"[File Saved] at {save_dir}")
        print("-"*30)
         
        return

    @staticmethod
    def preprocess_text_for_parlai(text):
        to_remove = ['text:', 'labels:', '__context_', '__tag_'
                     'label_candidates:', 'episode_done:', ':']
        for item in to_remove:
            text = text.replace(item, '')
        return text

    def create_500_tag_prediction_lines_parlai(
            self, basket, fixed_candidates
    ):
        lines = []
        text = basket["text"]
        tag_value_list = basket["tag_value_list"]
        tags = [x['tag'] for x in tag_value_list if x['tag'] in fixed_candidates]
        # cand = self.preprocess_text_for_parlai(cand)

        diff = set(set(fixed_candidates).difference(tags))

        negative_tags = []
        for tag in tags:
            elem = diff.pop()
            negative_tags.append(elem)

        for tag in tags:
            text = self.preprocess_text_for_parlai(text)
            tag = self.preprocess_text_for_parlai(tag)
            line = [f'text:__tag_ {tag} __context_ {text}',
                    f'labels:1',
                    'label_candidates:1|0',
                    'episode_done:True']
            line = "\t".join(line)
            lines.append(line)

        for neg_tag in negative_tags:
            text = self.preprocess_text_for_parlai(text)
            neg_tag = self.preprocess_text_for_parlai(neg_tag)

            line = [f'text:__tag_ {neg_tag} __context_ {text}',
                    f'labels:0',
                    'label_candidates:1|0',
                    'episode_done:True']
            line = "\t".join(line)
            lines.append(line)

        return lines

    def create_generation_lines_parlai(self, basket):
        text = basket["text"]
        text = text.split(" ")[:1023]
        text = " ".join(text)
        tag_value_list = basket["tag_value_list"]
        label = []
        for tag_value_dict in tag_value_list:
            label.append(
                f"__{tag_value_dict['tag']}_ {tag_value_dict['value']}"
            )
        label = " ".join(label)

        line = [f'text:{text}',
                f'labels:{label}',
                'episode_done:True']
        line = "\t".join(line)
        return line

    def create_fixed_candidates_for_tag_prediction(self,
                                                   doc_name2data,
                                                   create_new_file):
        """
        Args:
            doc_name2data: the dict ... (ref: generate_parlai_data)

        Returns:
            tag_list: a list of str, which is the list of tags

        This method also save the fixed candidates as a file at 'save_dir'
        """
        import os
        tag_count_dict = dict()
        save_dir = "fixed_candidates_for_tag_prediction.txt"
        if (create_new_file) and (not os.path.isfile(save_dir)):
            pass
        else:
            loader_ = TEXTLoader(save_dir)
            tag_list = loader_().split("\n")
            return [x for x in tag_list if x]

        for doc_name, basket_list in doc_name2data.items():
            for basket in basket_list:
                tags = [x['tag'] for x in basket['tag_value_list']]
                for tag in tags:
                    if tag in tag_count_dict:
                        tag_count_dict[tag] += 1
                    else:
                        tag_count_dict[tag] = 1

        tag_list = list(tag_count_dict.keys())
        tag_list = sorted(tag_list, key=lambda x: tag_count_dict[x], reverse=True)[:500]

        tag_list_text = ""
        for tag in tag_list:
            tag_list_text += tag 
            tag_list_text += "\n"

        saver = TEXTSaver(tag_list_text, save_dir)
        saver()
        print(f"[FILE SAVED] at {save_dir}")
        return tag_list

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
        sampler.generate_parlai_data()

        """
        ['500-tag-prediction',
             'value-generation',
             'value-offset-prediction']
        """

