#include<stdio.h>
#include<stdlib.h>
#include<string.h>

struct node{
    struct  node *lchild;
    int data;
    struct node *rchild;
}*root = NULL;

struct node *insert(struct node *p, int key){

    struct node *t = NULL;
    if(p==NULL){
        t = (struct node *)malloc(sizeof(struct node));
        t->data = key;
        t->lchild = t->rchild = NULL;
        return t;
    }
    if(key<p->data){
        p->lchild = insert(p->lchild, key);
    }
    else{
        p->rchild = insert(p->rchild, key);
    }
    return p;
}



void printLevel(struct node* root, int level) {
    if (root == NULL)
        return;
    if (level == 1)
        printf("%d ", root->data);
    else if (level > 1) {
        printLevel(root->lchild, level - 1);
        printLevel(root->rchild, level - 1);
    }
}

int height(struct node* node) {
    if (node == NULL)
        return 0;
    else {
        int leftHeight = height(node->lchild);
        int rightHeight = height(node->rchild);
        return (leftHeight > rightHeight) ? (leftHeight + 1) : (rightHeight + 1);
    }
}

void levelOrder(struct node* root) {
    int h = height(root);
    for (int i = 1; i <= h; i++) {
        printLevel(root, i);
    }
}

int main(){

    root = insert(root,10);
    insert(root,6);
    insert(root,5);
    insert(root,15);
    insert(root,27);

    levelOrder(root);
    printf("\n");
  return 0;
}