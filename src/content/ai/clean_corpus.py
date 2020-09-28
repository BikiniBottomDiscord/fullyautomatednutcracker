from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import torch
from torch.jit import script, trace
import torch.nn as nn
from torch import optim
import torch.nn.functional as F
import csv
import random
import re
import os
import unicodedata
import codecs
from io import open
import itertools
import math

channel = 479655334219087873
cleaned_messages = []
filtered_users = []
allowed_emojis = [479723952265232396, 479723952890052608, 479723972024467477, 479723979540791297, 479723980119343133, 479723980803014660, 479723982296186880, 479723983949004819, 479723984561373184, 479730735201255436, 479741478004850688, 479742330870431744, 481685935042592769, 502338448951083020, 507442547757416449, 516086632433057823, 516087135128911892, 521464153660194845, 521464154104791040, 522511018648141835, 525800702371692544, 525800702392532992, 525800708084203530, 525800708612554762, 545410833677549589, 545410902162407455, 545410991048097831, 545411030818357278, 545411074002780170, 545656193368981515, 548200365829521418, 548200386838659083, 548201567719784453, 557662431908986890, 566366943989334046, 566369173496659988, 585692885148631060, 585692885148631061, 585692885211676684, 585692885349957652, 585692887681990686, 585692888122392577, 585693091030237184, 585693091176906771, 585694894824357901, 585699019490066445, 585706335543492618, 585706336185090089, 585706336516571136, 585707249109041153, 585708011981635594, 585708821306146816, 588130927368994836, 588131165924229131, 588131741080879123, 589318185183084554, 589691208004141060, 589691208712847360, 589695048816263171, 590058725252005888, 591495036877668368, 592891749035409409, 594371282477514753, 602650379070603287, 602652571198554131, 605539673905037313, 611986028848349232, 611986038054846562, 611986038130475009, 611986039074193408, 611986040944590852, 611986040990990356, 613588180662485002, 615041291222384652, 642233324193972224, 642234025112633344, 642234025234399232, 642234025448177684, 642234025640984606, 642234025842573312, 642234025985179648, 642234354646384641, 642234458564591617, 642234573505298432, 642234799091875870, 642234897078943754, 646218812844277789, 646467004106276896, 648248865144963075, 654576835039985675, 654576835224535080, 654576835253895178, 654576835387981835, 654576835509747732, 654576835543433224, 654576835715268609, 654576835895492609, 654576835929178134, 654576836176510995, 654576836398809108, 672159558378192935, 673634603201724435, 673634603340267520, 673634603419959297, 673634603680137223, 677420452846764032, 677420453102616596, 693001359498412073, 693001359838150657, 693001359934357563, 693001360026894367, 693001360144334869, 693001360295198752, 693001360299261964, 693001360328884235, 693001360404250645, 693001360551051285, 693001360588931082, 693001360622485514, 693001360689332262, 693001361071013909, 709436310536061041, 718369340088516630, 718369340390506516, 718369340444901406, 718369340482781305, 718369340495495198, 718369340692365343, 718369340788834345, 718369341107863582, 718369341162258482, 718369341178904606, 718369341195943977, 718369341263052861, 718369341501866055, 718369341531226132, 718369341728489514, 718369341770563674, 718369341816700958, 718369341846061057, 718369341862707201, 718369342047387698, 718369342110040094, 718369342164697100, 718369342185799742, 718369342286331926, 718369342441521224, 718369342730928179, 718369342760288286, 718369342798037052, 718369342865145896, 718369342940643359, 718369343079186474, 718369343116673047, 718369343188238388, 718369343326650378, 718369343477383178, 718369343561269279, 718369764094771212, 718733566808424470, 718733633011318795, 718733801697705984, 733484459491328040, 745511392936984587, 745511392962019339, 745511393041580043, 745511393217740810, 745511393251295243, 745511393356152873, 745511393356415037, 745511393435844688, 745511393477918811, 745511393482244096, 745511394010464321, 745512433057005629, 745512433061462078, 745512433162125312, 745512433174577185, 745512433296343061, 745512433329897475, 745512433367646248, 745512433434493029, 745512433443012659, 745512433464115232, 745512433640276029, 745512433657053224, 745512433778556938, 745512433837408346, 745512433917100115, 745512433933877368, 745512433975820428, 745512434282004590, 745512434298650635, 745512434328141855, 745512434382405653, 745512434462359714, 745512434525143090, 745512434558828599, 745512434588057691, 745512434613092417, 745512434692784198, 745512434718212106, 745512434780864623, 745512434860556400, 745512434911150130, 745512434952831138, 745512435322060850, 748006588874489916, 751274102668656645]
max_sentence = 25
min_voc_word_count = 2

# Default word tokens
PAD_token = 0  # Used for padding short sentences
SOS_token = 1  # Start-of-sentence token
EOS_token = 2  # End-of-sentence token


USE_CUDA = torch.cuda.is_available()
device = torch.device("cuda" if USE_CUDA else "cpu")


class Voc:
    def __init__(self, name):
        self.name = name
        self.trimmed = False
        self.word2index = {}
        self.word2count = {}
        self.index2word = {PAD_token: "PAD", SOS_token: "SOS", EOS_token: "EOS"}
        self.num_words = 3  # Count SOS, EOS, PAD

    def add_sentence(self, sent):
        for word in sent.split(' '):
            self.add_word(word)

    def add_word(self, word):
        if word not in self.word2index:
            self.word2index[word] = self.num_words
            self.word2count[word] = 1
            self.index2word[self.num_words] = word
            self.num_words += 1
        else:
            self.word2count[word] += 1

    # Remove words below a certain count threshold
    def trim(self, min_count):
        if self.trimmed:
            return
        self.trimmed = True

        keep_words = []

        for k, v in self.word2count.items():
            if v >= min_count:
                keep_words.append(k)

        print('keep_words {} / {} = {:.4f}'.format(
            len(keep_words), len(self.word2index), len(keep_words) / len(self.word2index)
        ))

        # Reinitialize dictionaries
        self.word2index = {}
        self.word2count = {}
        self.index2word = {PAD_token: "PAD", SOS_token: "SOS", EOS_token: "EOS"}
        self.num_words = 3  # Count default tokens

        for word in keep_words:
            self.add_word(word)


class EncoderRNN(nn.Module):
    def __init__(self, hidden_size, embedding, n_layers=1, dropout=0):
        super(EncoderRNN, self).__init__()
        self.n_layers = n_layers
        self.hidden_size = hidden_size
        self.embedding = embedding

        # Initialize GRU; the input_size and hidden_size params are both set to 'hidden_size'
        #   because our input size is a word embedding with number of features == hidden_size
        self.gru = nn.GRU(hidden_size, hidden_size, n_layers,
                          dropout=(0 if n_layers == 1 else dropout), bidirectional=True)

    def forward(self, input_seq, input_lengths, hidden=None):
        # Convert word indexes to embeddings
        embedded = self.embedding(input_seq)
        # Pack padded batch of sequences for RNN module
        packed = nn.utils.rnn.pack_padded_sequence(embedded, input_lengths)
        # Forward pass through GRU
        outputs, hidden = self.gru(packed, hidden)
        # Unpack padding
        outputs, _ = nn.utils.rnn.pad_packed_sequence(outputs)
        # Sum bidirectional GRU outputs
        outputs = outputs[:, :, :self.hidden_size] + outputs[:, : ,self.hidden_size:]
        # Return output and final hidden state
        return outputs, hidden


# Luong attention layer
class Attn(nn.Module):
    def __init__(self, method, hidden_size):
        super(Attn, self).__init__()
        self.method = method
        if self.method not in ['dot', 'general', 'concat']:
            raise ValueError(self.method, "is not an appropriate attention method.")
        self.hidden_size = hidden_size
        if self.method == 'general':
            self.attn = nn.Linear(self.hidden_size, hidden_size)
        elif self.method == 'concat':
            self.attn = nn.Linear(self.hidden_size * 2, hidden_size)
            self.v = nn.Parameter(torch.FloatTensor(hidden_size))

    def dot_score(self, hidden, encoder_output):
        return torch.sum(hidden * encoder_output, dim=2)

    def general_score(self, hidden, encoder_output):
        energy = self.attn(encoder_output)
        return torch.sum(hidden * energy, dim=2)

    def concat_score(self, hidden, encoder_output):
        energy = self.attn(torch.cat((hidden.expand(encoder_output.size(0), -1, -1), encoder_output), 2)).tanh()
        return torch.sum(self.v * energy, dim=2)

    def forward(self, hidden, encoder_outputs):
        # Calculate the attention weights (energies) based on the given method
        if self.method == 'general':
            attn_energies = self.general_score(hidden, encoder_outputs)
        elif self.method == 'concat':
            attn_energies = self.concat_score(hidden, encoder_outputs)
        elif self.method == 'dot':
            attn_energies = self.dot_score(hidden, encoder_outputs)
        else:
            return

        # Transpose max_length and batch_size dimensions
        attn_energies = attn_energies.t()

        # Return the softmax normalized probability scores (with added dimension)
        return F.softmax(attn_energies, dim=1).unsqueeze(1)


class LuongAttnDecoderRNN(nn.Module):
    def __init__(self, attn_model, embedding, hidden_size, output_size, n_layers=1, dropout=0.1):
        super(LuongAttnDecoderRNN, self).__init__()

        # Keep for reference
        self.attn_model = attn_model
        self.hidden_size = hidden_size
        self.output_size = output_size
        self.n_layers = n_layers
        self.dropout = dropout

        # Define layers
        self.embedding = embedding
        self.embedding_dropout = nn.Dropout(dropout)
        self.gru = nn.GRU(hidden_size, hidden_size, n_layers, dropout=(0 if n_layers == 1 else dropout))
        self.concat = nn.Linear(hidden_size * 2, hidden_size)
        self.out = nn.Linear(hidden_size, output_size)

        self.attn = Attn(attn_model, hidden_size)

    def forward(self, input_step, last_hidden, encoder_outputs):
        # Note: we run this one step (word) at a time
        # Get embedding of current input word
        embedded = self.embedding(input_step)
        embedded = self.embedding_dropout(embedded)
        # Forward through unidirectional GRU
        rnn_output, hidden = self.gru(embedded, last_hidden)
        # Calculate attention weights from the current GRU output
        attn_weights = self.attn(rnn_output, encoder_outputs)
        # Multiply attention weights to encoder outputs to get new "weighted sum" context vector
        context = attn_weights.bmm(encoder_outputs.transpose(0, 1))
        # Concatenate weighted context vector and GRU output using Luong eq. 5
        rnn_output = rnn_output.squeeze(0)
        context = context.squeeze(1)
        concat_input = torch.cat((rnn_output, context), 1)
        concat_output = torch.tanh(self.concat(concat_input))
        # Predict next word using Luong eq. 6
        output = self.out(concat_output)
        output = F.softmax(output, dim=1)
        # Return output and final hidden state
        return output, hidden


# Turn a Unicode string to plain ASCII, thanks to
# https://stackoverflow.com/a/518232/2809427
def unicode_to_ascii(s):
    return ''.join(
        c for c in unicodedata.normalize('NFD', s)
        if unicodedata.category(c) != 'Mn'
    )


def filter_emojis(s):
    matches = re.findall(r"(<a?:\w*:\d*>)", s)
    for match in matches:
        _, __, emoji_id = match[1:-1].split(":")
        if emoji_id.isnumeric() and int(emoji_id) not in allowed_emojis:
            s = s.replace(match, " ")
        elif not emoji_id.isnumeric():
            pass
        else:
            s = s.replace(match, f"<e{emoji_id}e>")
    return s


def maxulate_string(s):
    words = s.split(' ')
    if len(words) > max_sentence:
        s = ' '.join(words[:max_sentence])
    return s


# Lowercase, trim, and remove non-letter characters
def normalize_string(s):
    s = s.lower().strip()
    # s = unicode_to_ascii(s.lower().strip())
    s = re.sub(r'''(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))''', r" ", s)
    s = filter_emojis(s)
    s = s.replace("<@!", "<@")
    s = re.sub(r"[^a-zA-Z.!?<>:0-9@#\\]+", r" ", s)
    s = re.sub(r"([.!?])", r" \1 ", s)
    s = re.sub(r"\s+", r" ", s).strip()
    s = maxulate_string(s)
    return s


def maskNLLLoss(inp, target, mask):
    nTotal = mask.sum()
    crossEntropy = -torch.log(torch.gather(inp, 1, target.view(-1, 1)).squeeze(1))
    loss = crossEntropy.masked_select(mask).mean()
    loss = loss.to(device)
    return loss, nTotal.item()


def train(input_variable, lengths, target_variable, mask, max_target_len, encoder, decoder, embedding,
          encoder_optimizer, decoder_optimizer, batch_size, clip, max_length=max_sentence):

    # Zero gradients
    encoder_optimizer.zero_grad()
    decoder_optimizer.zero_grad()

    # Set device options
    input_variable = input_variable.to(device)
    lengths = lengths.to(device)
    target_variable = target_variable.to(device)
    mask = mask.to(device)

    # Initialize variables
    loss = 0
    print_losses = []
    n_totals = 0

    # Forward pass through encoder
    encoder_outputs, encoder_hidden = encoder(input_variable, lengths)

    # Create initial decoder input (start with SOS tokens for each sentence)
    decoder_input = torch.LongTensor([[SOS_token for _ in range(batch_size)]])
    decoder_input = decoder_input.to(device)

    # Set initial decoder hidden state to the encoder's final hidden state
    decoder_hidden = encoder_hidden[:decoder.n_layers]

    # Determine if we are using teacher forcing this iteration
    use_teacher_forcing = True if random.random() < teacher_forcing_ratio else False

    # Forward batch of sequences through decoder one time step at a time
    if use_teacher_forcing:
        for t in range(max_target_len):
            decoder_output, decoder_hidden = decoder(
                decoder_input, decoder_hidden, encoder_outputs
            )
            # Teacher forcing: next input is current target
            decoder_input = target_variable[t].view(1, -1)
            # Calculate and accumulate loss
            mask_loss, nTotal = maskNLLLoss(decoder_output, target_variable[t], mask[t])
            loss += mask_loss
            print_losses.append(mask_loss.item() * nTotal)
            n_totals += nTotal
    else:
        for t in range(max_target_len):
            decoder_output, decoder_hidden = decoder(
                decoder_input, decoder_hidden, encoder_outputs
            )
            # No teacher forcing: next input is decoder's own current output
            _, topi = decoder_output.topk(1)
            decoder_input = torch.LongTensor([[topi[i][0] for i in range(batch_size)]])
            decoder_input = decoder_input.to(device)
            # Calculate and accumulate loss
            mask_loss, nTotal = maskNLLLoss(decoder_output, target_variable[t], mask[t])
            loss += mask_loss
            print_losses.append(mask_loss.item() * nTotal)
            n_totals += nTotal

    # Perform backpropatation
    loss.backward()

    # Clip gradients: gradients are modified in place
    _ = nn.utils.clip_grad_norm_(encoder.parameters(), clip)
    _ = nn.utils.clip_grad_norm_(decoder.parameters(), clip)

    # Adjust model weights
    encoder_optimizer.step()
    decoder_optimizer.step()

    return sum(print_losses) / n_totals


def trainIters(model_name, voc, pairs, encoder, decoder, encoder_optimizer, decoder_optimizer, embedding, encoder_n_layers, decoder_n_layers, save_dir, n_iteration, batch_size, print_every, save_every, clip, corpus_name, loadFilename):

    # Load batches for each iteration
    training_batches = [batch2TrainData(voc, [random.choice(pairs) for _ in range(batch_size)])
                      for _ in range(n_iteration)]

    # Initializations
    print('Initializing ...')
    start_iteration = 1
    print_loss = 0
    if loadFilename:
        start_iteration = checkpoint['iteration'] + 1

    # Training loop
    print("Training...")
    for iteration in range(start_iteration, n_iteration + 1):
        training_batch = training_batches[iteration - 1]
        # Extract fields from batch
        input_variable, lengths, target_variable, mask, max_target_len = training_batch

        # Run a training iteration with batch
        loss = train(input_variable, lengths, target_variable, mask, max_target_len, encoder,
                     decoder, embedding, encoder_optimizer, decoder_optimizer, batch_size, clip)
        print_loss += loss

        # Print progress
        if iteration % print_every == 0:
            print_loss_avg = print_loss / print_every
            print("Iteration: {}; Percent complete: {:.1f}%; Average loss: {:.4f}".format(iteration, iteration / n_iteration * 100, print_loss_avg))
            print_loss = 0

        # Save checkpoint
        if (iteration % save_every == 0):
            directory = os.path.join(save_dir, model_name, corpus_name, '{}-{}_{}'.format(encoder_n_layers, decoder_n_layers, hidden_size))
            if not os.path.exists(directory):
                os.makedirs(directory)
            torch.save({
                'iteration': iteration,
                'en': encoder.state_dict(),
                'de': decoder.state_dict(),
                'en_opt': encoder_optimizer.state_dict(),
                'de_opt': decoder_optimizer.state_dict(),
                'loss': loss,
                'voc_dict': voc.__dict__,
                'embedding': embedding.state_dict()
            }, os.path.join(directory, '{}_{}.tar'.format(iteration, 'checkpoint')))


with open(f"{channel}.log", "r", encoding='utf-8') as fp:
    curr_message = ""
    for line in fp.readlines():
        if line.lstrip().split(',')[0] == "384811165949231104" and curr_message != "":
            if int(curr_message.split(',')[3]) not in filtered_users:
                normalized = normalize_string(curr_message[:-4][103:])
                if normalized.strip() != "":
                    cleaned_messages.append(normalized)
            curr_message = ""
        curr_message += line.replace("\n", " \\n ")


voc = Voc(f"{channel}.voc.log")
for sentence in cleaned_messages:
    voc.add_sentence(sentence)

pairs = []

print("Counted words:", voc.num_words)
voc.trim(min_voc_word_count)
print("Trimmed Counted words:", voc.num_words)


with open(f"{channel}.cleaned.log", "w", encoding='utf-8') as fp:
    for msg in cleaned_messages:
        fp.write(msg + "\n")
