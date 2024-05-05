class Parent {
    void method() throws Exception {
        System.out.println("Parent's method");
    }
}

class Child extends Parent {
    @Override
    void method() throws Exception {
        System.out.println("Child's method");
        throw new Exception("Exception from Child's method");
    }
}

public class InheritanceExceptionExample {
    public static void main(String[] args) {
        try {
            Parent obj = new Child();
            obj.method();
        } catch (Exception e) {
            System.out.println("Exception caught: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
